from typing import List

import polars as pl

from ..._types import SourceColDef, ThresholdLevel
from ..._types.error import ValidationResult, StructureValidationError
from ..._utils.sanitize import sanitise_column_headers

# _INTERNAL_COL_PATTERN = r'meta__.*'
# %%


def _rename_columns_from_aliases(
    lf: pl.LazyFrame, *, aliases: dict[str, str], schema_name: str
) -> ValidationResult:
    """
     Rename columns in a LazyFrame based on a dictionary of aliases.

    :param lf: Polars LazyFrame
    :param aliases: Dictionary of column aliases
    :param schema_name: Name of the schema
    :return:
    """

    errors = []

    normalised_lf = sanitise_column_headers(lf)
    source_columns = normalised_lf.collect_schema().names()

    assigned_targets = set()
    rename_cols = {}

    for source in source_columns:
        target = aliases.get(source, source)
        # Only rename if the target is not in the source columns
        if target not in source_columns:
            # If the target is already assigned, then it is a duplicate
            if target in assigned_targets:
                errors.append(
                    StructureValidationError(
                        schema=schema_name,
                        column=source,
                        error="duplicate_column",
                        level=ThresholdLevel.REJECT.level,
                        message=f"Column '{target}' has a duplicated alias ('{source}')",
                    )
                )
            # No need to rename if source and target are the same
            elif target != source:
                rename_cols[source] = target

        assigned_targets.add(target)

    for old_col, new_col in rename_cols.items():
        errors.append(
            StructureValidationError(
                schema=schema_name,
                column=new_col,
                error="renamed_column",
                level=ThresholdLevel.WARNING.level,
                message=f"Renamed '{old_col}' to '{new_col}'",
            )
        )

    return ValidationResult(data=normalised_lf.rename(rename_cols), errors=errors)


# %%


def _remove_null_rows(lf: pl.LazyFrame) -> pl.LazyFrame:
    return lf.filter(~pl.all_horizontal(pl.all().is_null()))


# %%


def _check_critical_columns(
    data_cols: list[str], *, col_defs: List[SourceColDef], schema_name: str
) -> list[StructureValidationError]:
    critical_cols = {
        c.name: c.if_missing for c in col_defs if c.if_missing == ThresholdLevel.REJECT
    }
    return [
        StructureValidationError(
            schema=schema_name,
            column=col_key,
            error="required_column",
            level=lvl.level,
            message=f"Column '{col_key}' is required but missing from  from the data",
        )
        for col_key, lvl in critical_cols.items()
        if col_key not in data_cols
    ]


def _check_non_critical_columns(
    data_cols: list[str], *, col_defs: List[SourceColDef], schema_name: str
) -> list[StructureValidationError]:
    non_critical_cols = {
        c.name: c.if_missing
        for c in col_defs
        if c.if_missing != ThresholdLevel.REJECT and c.if_missing is not None
    }
    return [
        StructureValidationError(
            schema=schema_name,
            column=col_key,
            error="missing_column",
            level=lvl.level,
            message=f"Column '{col_key}' is missing from the data",
        )
        for col_key, lvl in non_critical_cols.items()
        if col_key not in data_cols
    ]


def _check_extra_columns(
    data_cols: list[str], *, col_defs: List[SourceColDef], schema_name: str
) -> list[StructureValidationError]:
    all_cols = {c.name for c in col_defs}
    return [
        StructureValidationError(
            schema=schema_name,
            column=c,
            error="extra_column",
            level=ThresholdLevel.WARNING.level,
            message=f"Column '{c}' is additional and not required",
        )
        for c in data_cols
        if c not in all_cols  # and not re.match(_INTERNAL_COL_PATTERN, c)
    ]


# %%


def _normalise_table_structure(
    lf: pl.LazyFrame, col_defs: List[SourceColDef], schema_name: str
) -> ValidationResult:
    """
    Normalise the structure of a table based on the column definitions.

    :param lf: Polars LazyFrame
    :param schema_name: The name of the schema
    :param col_defs: List of Column Schema definitions
    :return:
    """
    errors: list[StructureValidationError] = []
    missing_cols: list[StructureValidationError] = []
    data_cols = lf.collect_schema().names()

    critical_errors = _check_critical_columns(
        data_cols, col_defs=col_defs, schema_name=schema_name
    )
    missing_cols.extend(critical_errors)

    non_critical = _check_non_critical_columns(
        data_cols, col_defs=col_defs, schema_name=schema_name
    )
    missing_cols.extend(non_critical)

    if len(missing_cols) > 0:
        lf = lf.with_columns(
            [pl.lit(None).cast(pl.String).alias(mc.column) for mc in missing_cols]
        )
        errors.extend(missing_cols)

    extra_cols = _check_extra_columns(
        data_cols, col_defs=col_defs, schema_name=schema_name
    )

    # if lf has extra columns, drop them
    if len(extra_cols) > 0:
        lf = lf.drop([c.column for c in extra_cols])
        errors.extend(extra_cols)

    is_empty = (
        lf.select([c.name for c in col_defs])
        .pipe(_remove_null_rows)
        .limit(1)
        .collect()
        .is_empty()
    )
    if is_empty:
        errors.append(
            StructureValidationError(
                schema=schema_name,
                error="empty_data",
                level=ThresholdLevel.REJECT.level,
                message=f"`{schema_name}` has no data after additional/unused columns have been removed",
            )
        )

    return ValidationResult(data=lf, errors=errors)


# %%
def normalise_column_headers(
    lf: pl.LazyFrame, col_defs: List[SourceColDef], schema_name: str
) -> ValidationResult:
    """
    Normalise the column headers of a table to a common structure based on the column definitions.
    :param lf: Polars LazyFrame
    :param col_defs: Column definitions (from a TableSchema)
    :param schema_name: Name of the schema
    :return:
    """
    errors = []
    reject = False
    schema_aliases = {a: c.name for c in col_defs for a in c.aliases}
    sanitised = _rename_columns_from_aliases(
        lf, aliases=schema_aliases, schema_name=schema_name
    )
    errors.extend(sanitised.errors)

    normalised = _normalise_table_structure(
        sanitised.data, col_defs=col_defs, schema_name=schema_name
    )
    errors.extend(normalised.errors)

    for e in errors:
        if e.level == ThresholdLevel.REJECT.level:
            reject = True
            break

    return ValidationResult(data=normalised.data, errors=errors, reject=reject)
