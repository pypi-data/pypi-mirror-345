from dataclasses import dataclass, field, replace
from typing import List, Literal

from polars import LazyFrame

from ._utils.normalise import normalise_column_headers
from .._types import ColumnNode, SourceColDef, ThresholdLevel
from .._types.error import ValidationResult, ProcessingResult
from .._utils.args import _flatten_args
from ..column.col import ColumnSchema
from ..registry import ColumnRegistry, generate_optimized_stages


@dataclass(frozen=True, kw_only=True)
class _SchemaParams:
    name: str
    is_required: bool = False
    stage: str | None = None
    source_columns: dict[str, SourceColDef] = field(default_factory=dict)
    registry: ColumnRegistry = field(default_factory=ColumnRegistry)


class TableSchema:
    """
    Defines a table schema for data validation and processing.

    Parameters:
        name (str): Name of the schema.
        is_required (bool): Whether the schema is required.
        columns (List[ColumnSchema], optional): List of column schemas.
        stage (str, optional): Processing stage.

    Usage:
        schema = TableSchema("demo", columns=[...])
    """

    def __init__(
        self,
        name: str,
        *,
        is_required: bool = False,
        columns: List[ColumnSchema] | None = None,
        stage: str | None = None,
    ):
        nodes = _cols_to_nodes(schema=name, stage=stage, columns=columns)

        self._params = _SchemaParams(
            name=name,
            is_required=is_required,
            stage=stage,
            registry=ColumnRegistry(nodes),
            source_columns=_cols_to_sources(columns),
        )

    def columns(
        self,
        *args: List[ColumnSchema] | ColumnSchema,
        method: Literal["merge", "replace"] = "merge",
    ) -> "TableSchema":
        columns = _flatten_args(args)
        if method == "merge":
            new_nodes = _cols_to_nodes(
                self._params.name, self._params.stage, columns=columns
            )

            new_registry = _reset_registry(self._params.registry.nodes() + new_nodes)

            new_source_columns = {
                **self._params.source_columns,
                **_cols_to_sources(columns),
            }
            return self._replace(
                registry=new_registry, source_columns=new_source_columns
            )

        elif method == "replace":
            new_registry = _reset_registry(
                _cols_to_nodes(self._params.name, self._params.stage, columns=columns)
            )
            new_source_columns = _cols_to_sources(columns)
            return self._replace(
                registry=new_registry, source_columns=new_source_columns
            )
        else:
            raise ValueError(f"Invalid method: {method}")

    def step_1_normalise(self, lf: LazyFrame) -> ValidationResult:
        """Normalise the headers of the lazy frame"""
        source_columns = list(self._params.source_columns.values())
        return normalise_column_headers(
            lf.lazy(), schema_name=self._params.name, col_defs=source_columns
        )

    def step_2_prepare(self, lf: LazyFrame) -> ValidationResult:
        prepped = lf

        stages = generate_optimized_stages(self._params.registry.nodes())

        for stage in stages:
            prepped = prepped.with_columns([c.expression for c in stage])

        # TODO: Add a check to see if the processing stages succeed
        return ValidationResult(data=prepped, errors=[], reject=False)

    def step_3_validate(self, lf: LazyFrame) -> ValidationResult:
        validation_errors = []
        for c in self._params.registry.nodes():
            if c.validation_rule is None:
                continue
            check = c.validation_rule.validate(lf)
            if check is not None:
                validation_errors.append(c.validation_rule.validate(lf))

        reject = False
        for e in validation_errors:
            if e.level == ThresholdLevel.REJECT.level:
                reject = True
                break

        return ValidationResult(data=lf, errors=validation_errors, reject=reject)

    def process_data(self, lf: LazyFrame) -> ProcessingResult:
        """Process the lazy frame through the schema"""
        errors = []
        normalised = self.step_1_normalise(lf)
        errors.extend(normalised.errors)
        if normalised.reject:
            return ProcessingResult(
                data=normalised.data,
                errors=errors,
                success=False,
                stage_failed="normalise",
            )

        prepped = self.step_2_prepare(normalised.data)
        errors.extend(prepped.errors)
        if prepped.reject:
            return ProcessingResult(
                data=prepped.data, errors=errors, success=False, stage_failed="prepare"
            )

        valid = self.step_3_validate(prepped.data)
        errors.extend(valid.errors)

        return ProcessingResult(
            data=valid.data,
            errors=errors,
            success=False if valid.reject else True,
            stage_failed="validate" if valid.reject else None,
        )

    def _replace(self, **kwargs):
        if "registry" not in kwargs:
            stage = kwargs.get("stage", self._params.stage)
            name = kwargs.get("name", self._params.name)
            kwargs["registry"] = ColumnRegistry(
                [
                    replace(n, stage=stage, schema=name)
                    for n in self._params.registry.nodes()
                ]
            )

        new_params = replace(self._params, **kwargs)
        return TableSchema(name=new_params.name).__set_params(new_params)

    def __set_params(self, params: _SchemaParams) -> "TableSchema":
        self._params = params
        return self


def _cols_to_nodes(
    schema: str, stage: str | None = None, columns: List[ColumnSchema] | None = None
) -> List[ColumnNode]:
    nodes = []
    if columns is None:
        return nodes

    for c in columns:
        assert isinstance(c, ColumnSchema), (
            f"All columns must be a Column Schema definition - {c}"
        )
        nodes.extend(c.get_nodes(schema, stage))

    return nodes


def _cols_to_sources(columns: List[ColumnSchema] | None) -> dict[str, SourceColDef]:
    sources = {}
    if columns is None:
        return sources
    for c in columns:
        if c.has_expression:
            # if a column has an expression, it is not a source column
            continue

        ref = c.ref

        if ref.name in sources:
            raise ValueError(f"Duplicate source column name: {ref.name}")
        else:
            sources[ref.name] = SourceColDef(
                name=ref.name, aliases=c.get_aliases, if_missing=c.if_missing
            )

    return sources


def _reset_registry(nodes: List[ColumnNode], **kwargs):
    return ColumnRegistry([replace(n, **kwargs) for n in nodes])
