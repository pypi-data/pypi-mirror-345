from dataclasses import dataclass, field, KW_ONLY
from typing import Any
import polars as pl

from ..._types import Sensitivity, ColumnDataType
from ..._utils.parse_dates import mega_date_handler
from ..._utils.sanitize import (
    SanitiseLevel,
    SanitiseLevelType,
    sanitise_scalar_string,
    full_sanitise_string_col,
    sanitise_string_col,
)
from .._utils.reference import ColumnRef

default_data_types = {
    "string": pl.String,
    "number": pl.Int64,
    "boolean": pl.Boolean,
    "date": pl.Date,
    "datetime": pl.Datetime,
    "duration": pl.Duration,
}


def _get_column_names(source: "ColumnRef") -> tuple[str, str]:
    source_column = source.name
    # alias = self.alias if self.alias is not None else source.clean().name
    alias = source.clean().name
    return source_column, alias


@dataclass(frozen=True)
class CleanColumn:
    _: KW_ONLY
    data_type: ColumnDataType = field(default="string")
    col_sensitivity: Sensitivity | None = field(default=None)

    # alias: str | None = field(default=None)

    def clean_ref(self, source: "ColumnRef") -> "ColumnRef":
        return source.clean()

    def clean_expr(self, source: "ColumnRef") -> pl.Expr:
        source_column, alias = _get_column_names(source)

        return pl.col(source_column).cast(pl.String).alias(alias)


@dataclass(frozen=True)
class StringColumn(CleanColumn):
    _: KW_ONLY
    sanitize: SanitiseLevelType = field(default=None)
    sanitise_join_char: str = field(default="_")

    def __post_init__(self):
        if self.sanitize is not None:
            assert self.sanitize in SanitiseLevel, (
                f"sanitize must be one of: {', '.join(f"'{s}'" for s in SanitiseLevel)} or None"
            )

    def _sanitise(self, source_column: str) -> pl.Expr:
        return sanitise_string_col(
            source_column,
            sanitize_level=self.sanitize,
            join_char=self.sanitise_join_char,
        )

    def clean_expr(self, source: "ColumnRef") -> pl.Expr:
        source_column, alias = _get_column_names(source)
        return self._sanitise(source_column).alias(alias)


# @dataclass(frozen=True)
# class SanitisedStringColumn(StringColumn):
#     data_type = "sanitised_string"
#     _: KW_ONLY
#     sanitise_join_char: str = "_"

#     def clean(self) -> pl.Expr:
#         return sanitise_string_col(self._source,  alias=self._alias, join_char=self.sanitise_join_char,)


@dataclass(frozen=True)
class CleanNumberColumn(CleanColumn):
    data_type = "number"
    _: KW_ONLY
    output_format: pl.Int64 | pl.Float64 = field(default=pl.Int64)

    def clean_expr(self, source: "ColumnRef") -> pl.Expr:
        source_column, alias = _get_column_names(source)
        return pl.col(source_column).cast(self.output_format, strict=False).alias(alias)


@dataclass(frozen=True)
class CleanBooleanColumn(CleanColumn):
    data_type = "boolean"
    _: KW_ONLY
    true_values: frozenset[Any] = field(default=frozenset({"yes", "true", "1"}))
    false_values: frozenset[Any] = field(default=frozenset({"no", "false", "0"}))

    _bool_map: dict[str, bool] = field(init=False)

    def __post_init__(self):
        if self.true_values is not None:
            assert isinstance(self.true_values, (set, frozenset)), (
                "true_values must be a set or frozenset"
            )
        if self.false_values is not None:
            assert isinstance(self.false_values, (set, frozenset)), (
                "false_values must be a set or frozenset"
            )

        sanitized_true = frozenset(
            sanitise_scalar_string(val) for val in self.true_values
        )
        sanitized_false = frozenset(
            sanitise_scalar_string(val) for val in self.false_values
        )

        if any(value in sanitized_false for value in sanitized_true):
            raise ValueError(
                f"true_values and false_values must be disjoint sets: {sanitized_true} and {sanitized_false}"
            )

        object.__setattr__(
            self,
            "_bool_map",
            {
                **{val: True for val in sanitized_true},
                **{val: False for val in sanitized_false},
            },
        )

    def clean_expr(self, source: "ColumnRef") -> pl.Expr:
        source_column, alias = _get_column_names(source)
        return (
            full_sanitise_string_col(source_column)
            .replace(self._bool_map, default=None, return_dtype=pl.Boolean)
            .alias(alias)
        )


@dataclass(frozen=True)
class CleanDateColumn(CleanColumn):
    data_type = "date"
    _: KW_ONLY
    output_format: pl.Date | pl.Datetime = field(default=pl.Date)

    def __post_init__(self):
        if self.output_format not in [pl.Date, pl.Datetime]:
            raise ValueError("output_format must be either pl.Date or pl.Datetime")

        if self.output_format == pl.Datetime:
            object.__setattr__(self, "data_type", "datetime")

    def clean_expr(self, source: "ColumnRef") -> pl.Expr:
        source_column, alias = _get_column_names(source)
        return mega_date_handler(
            source_column, alias=alias, output_format=self.output_format
        )


@dataclass(frozen=True)
class CleanEnumColumn(StringColumn):
    data_type = "enum"
    _: KW_ONLY
    enum_map: dict[str, Any] = field(default=None)
    no_match_value: str | None = "No Data"

    def __post_init__(self):
        assert isinstance(self.enum_map, dict), "enum_map must be a dictionary"

        # if we are sanitizing the column, we need to make sure the enum keys are also sanitized
        object.__setattr__(
            self,
            "enum_map",
            _clean_enum_keys(
                self.enum_map,
                sanitize=self.sanitize,
                sanitise_join_char=self.sanitise_join_char,
            ),
        )

    def clean_expr(self, source: "ColumnRef") -> pl.Expr:
        source_column, alias = _get_column_names(source)
        unique_values = set(self.enum_map.values())
        unique_values.add(self.no_match_value)

        return (
            self._sanitise(source_column)
            .replace(
                self.enum_map,
                default=self.no_match_value,
                return_dtype=pl.Enum(list(unique_values)),
            )
            .alias(alias)
        )


@dataclass(frozen=True)
class CleanIdColumn(StringColumn):
    data_type = "id"
    _: KW_ONLY
    prefix: ColumnRef | str | None = None
    separator: str = "::"

    def clean_expr(self, source: "ColumnRef") -> pl.Expr:
        source_column, alias = _get_column_names(source)

        if self.prefix is not None:
            prefix_expr = (
                pl.col(self.prefix.name)
                .cast(pl.String)
                .str.strip_chars()
                .str.to_lowercase()
                if isinstance(self.prefix, ColumnRef)
                else pl.lit(str(self.prefix).strip().lower())
            )
            return (prefix_expr + self.separator + self._sanitise(source_column)).alias(
                alias
            )
        else:
            return self._sanitise(source_column).alias(alias)


type CleanStage = (
    CleanColumn
    | StringColumn
    | CleanNumberColumn
    | CleanBooleanColumn
    | CleanDateColumn
    | CleanEnumColumn
    | CleanIdColumn
)


# ---------------------------------------------------------------------------------------------------


def _sanitize_and_validate_keys(
    enum_map: dict[str, Any], sanitize_fn: callable
) -> dict[str, str]:
    sanitized_map = {}
    for k, v in enum_map.items():
        sanitized_key = sanitize_fn(k)
        if sanitized_key in sanitized_map and sanitized_map[sanitized_key] != v:
            raise ValueError(
                f"Duplicate sanitized keys found: '{k}' and '{list(enum_map.keys())[list(sanitized_map.keys()).index(sanitized_key)]}' both sanitize to '{sanitized_key}' but have different values: '{v}' and '{sanitized_map[sanitized_key]}'"
            )
        sanitized_map[sanitized_key] = v
    return sanitized_map


def _clean_enum_keys(
    enum_map: dict[str, Any], *, sanitize: SanitiseLevelType, sanitise_join_char: str
) -> dict[str, str]:
    if sanitize == SanitiseLevel.FULL:
        return _sanitize_and_validate_keys(
            enum_map, lambda k: sanitise_scalar_string(k, join_char=sanitise_join_char)
        )
    elif sanitize == SanitiseLevel.LOWERCASE:
        return _sanitize_and_validate_keys(enum_map, lambda k: k.lower().strip())
    elif sanitize == SanitiseLevel.TRIM:
        return _sanitize_and_validate_keys(enum_map, lambda k: k.strip())
    else:
        return enum_map
