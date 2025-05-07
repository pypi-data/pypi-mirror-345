from typing import Union, List, Set, KeysView, Literal

import polars as pl

from ..._types import ThresholdLevel
from ..._utils.sanitize import full_sanitise_string_col

ROW_VALIDATION_SUCCESS_VALUE = ThresholdLevel.PASS.level

"""
---------------------------------------------------------------------------------------------
    Validator functions
---------------------------------------------------------------------------------------------
These functions check the column to check it is valid
"""


def _error_as_value(check: pl.Expr, error: str) -> pl.Expr:
    enum_def = pl.Enum([ROW_VALIDATION_SUCCESS_VALUE, error])

    return (
        pl.when(check)
        .then(pl.lit(ROW_VALIDATION_SUCCESS_VALUE))
        .otherwise(pl.lit(error))
        .cast(enum_def, strict=False)
    )


def check_col_row_not_empty(
    col: str,
    *,
    prefix: str = "",
    alias: str = None,
    str_check=False,
    error_as_value: None | str = None,
) -> pl.Expr:
    check = (
        (
            pl.col(col).is_not_null()
            & (full_sanitise_string_col(col).str.len_chars() > 0)
        )
        if str_check
        else pl.col(col).is_not_null()
    )
    a = alias if alias else f"{prefix}is_{col}_not_empty"
    if error_as_value is not None:
        return _error_as_value(check, error_as_value).alias(a)
    else:
        return check.alias(a)


def check_col_row_is_unique(
    col: str, *, prefix: str = "", alias: str = None, error_as_value: None | str = None
) -> pl.Expr:
    a = alias if alias else f"{prefix}is_{col}_unique"
    if error_as_value is not None:
        return _error_as_value(pl.col(col).is_unique(), error_as_value).alias(a)
    else:
        return pl.col(col).is_unique().alias(a)


_EnumMatchesType = Union[List[str], Set[str], KeysView[str]]
_MatchReturnType = Literal["match", "boolean", "error"]


def check_enum_match(
    col: str,
    *,
    prefix: str = "",
    alias: str = None,
    matches: _EnumMatchesType,
    sanitize: bool = True,
    return_type: _MatchReturnType = "match",
    error_value: str = "__NO_MATCH__",
) -> pl.Expr:
    if sanitize:
        return (
            pl.when(pl.col(col).is_null())
            .then(pl.lit(None))
            .when(full_sanitise_string_col(col).is_in(matches))
            .then(
                pl.lit(True)
                if return_type == "boolean"
                else full_sanitise_string_col(col)
            )
            .otherwise(pl.lit(False if return_type == "boolean" else error_value))
            .alias(alias if alias else f"{prefix}{col}_enum_match")
        )

    else:
        return (
            pl.when(pl.col(col).is_null())
            .then(pl.lit(None))
            .when(pl.col(col).is_in(matches))
            .then(pl.lit(True) if return_type == "boolean" else pl.col(col))
            .otherwise(pl.lit(False if return_type == "boolean" else "__NO_MATCH__"))
            .alias(alias if alias else f"{prefix}{col}_enum_match")
        )
