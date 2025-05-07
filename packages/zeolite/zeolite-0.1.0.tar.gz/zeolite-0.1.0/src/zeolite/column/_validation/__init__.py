from dataclasses import dataclass, field, KW_ONLY
from enum import Enum

import polars as pl

from .check_base import RowCheckBase
from .data_checks import (
    ROW_VALIDATION_SUCCESS_VALUE,
    check_col_row_is_unique,
    check_col_row_not_empty,
)
from ..._types.validation.threshold import CheckLevel


class RowCheckType(Enum):
    IS_EMPTY = "is_empty"
    IS_DUPLICATED = "is_duplicated"
    IS_INVALID_DATE = "is_invalid_date"
    IS_EQUAL_TO = "is_equal_to"


@dataclass(frozen=True)
class IsValueEmpty(RowCheckBase):
    """
    Validation check: Ensures that column values are not empty or null.

    Parameters:
        exclude_row (bool): Whether to exclude rows with empty values.
        check_on_cleaned (bool): Whether to check on cleaned column or the original.

        thresholds (Threshold): Thresholds for error capturing when the table is processed.
        warning (CheckThreshold): Warning threshold (used when no thresholds are provided).
        error (CheckThreshold): Error threshold (used when no thresholds are provided).
        reject (CheckThreshold): Reject threshold (used when no thresholds are provided).

        treat_empty_strings_as_null (bool): Whether to treat empty strings as null.
        message (str): Error message template.
    """

    @classmethod
    def method_id(cls) -> str:
        return RowCheckType.IS_EMPTY.value

    treat_empty_strings_as_null: bool = False
    message: str = field(
        default="{{column}} has {{count}} null (empty) value(s) ({{fraction}})"
    )

    def _check_expression(
        self, source_column: str, alias: str, level: CheckLevel
    ) -> pl.Expr:
        return check_col_row_not_empty(
            source_column,
            alias=alias,
            str_check=self.treat_empty_strings_as_null,
            error_as_value=level,
        )


@dataclass(frozen=True)
class IsValueDuplicated(RowCheckBase):
    """
    Validation check: Ensures that column values are unique.

    Parameters:
    exclude_row (bool): Whether to exclude rows with empty values.
        check_on_cleaned (bool): Whether to check on cleaned column or the original.
        thresholds (Threshold): Thresholds for error capturing when the table is processed.
        warning (CheckThreshold): Warning threshold (used when no thresholds are provided).
        error (CheckThreshold): Error threshold (used when no thresholds are provided).
        reject (CheckThreshold): Reject threshold (used when no thresholds are provided).
        message (str): Error message template.
    """

    @classmethod
    def method_id(cls) -> str:
        return RowCheckType.IS_DUPLICATED.value

    message: str = field(
        default="{{column}} has {{count}} duplicate value(s) ({{fraction}})"
    )

    def _check_expression(
        self, source_column: str, alias: str, level: CheckLevel
    ) -> pl.Expr:
        return check_col_row_is_unique(source_column, alias=alias, error_as_value=level)


@dataclass(frozen=True)
class IsValueInvalidDate(RowCheckBase):
    """
    Validation check: Ensures that column values are valid dates - essentially checks
    for nulls in a date data-type column.

    Parameters:
        exclude_row (bool): Whether to exclude rows with empty values.
        check_on_cleaned (bool): Whether to check on cleaned column or the original.
        thresholds (Threshold): Thresholds for error capturing when the table is processed.
        warning (CheckThreshold): Warning threshold (used when no thresholds are provided).
        error (CheckThreshold): Error threshold (used when no thresholds are provided).
        reject (CheckThreshold): Reject threshold (used when no thresholds are provided).
        message (str): Error message template.
    """

    @classmethod
    def method_id(cls) -> str:
        return RowCheckType.IS_INVALID_DATE.value

    check_on_cleaned: bool = True
    message: str = field(
        default="{{column}} has {{count}} invalid date(s) ({{fraction}})"
    )

    def _check_expression(
        self, source_column: str, alias: str, level: CheckLevel
    ) -> pl.Expr:
        return check_col_row_not_empty(
            source_column, alias=alias, str_check=False, error_as_value=level
        )


@dataclass(frozen=True)
class IsValueEqualTo(RowCheckBase):
    """
    Validation check: Ensures that column values are (not) equal to a specified value. This will
    throw an error if the value IS FOUND in the column.

    Parameters:
        value (str | int | float | bool): The value to check against.
        exclude_row (bool): Whether to exclude rows with empty values.
        check_on_cleaned (bool): Whether to check on cleaned column or the original.
        thresholds (Threshold): Thresholds for error capturing when the table is processed.
        warning (CheckThreshold): Warning threshold (used when no thresholds are provided).
        error (CheckThreshold): Error threshold (used when no thresholds are provided).
        reject (CheckThreshold): Reject threshold (used when no thresholds are provided).
        message (str): Error message template.
    """

    @classmethod
    def method_id(cls) -> str:
        return RowCheckType.IS_EQUAL_TO.value

    value: str | int | float | bool = None
    _: KW_ONLY
    check_on_cleaned: bool = False
    message: str = field(
        default="{{column}} has {{count}} value(s) equal to '{{match_value}}' ({{fraction}})"
    )

    def __post_init__(self):
        assert self.value is not None, "Must provide a value to check against"
        object.__setattr__(
            self, "_label", f"{self.method_id()}_{self.value}".lower().replace(" ", "_")
        )
        object.__setattr__(
            self, "message", self.message.replace("{{match_value}}", str(self.value))
        )
        super().__post_init__()

    def _check_expression(
        self, source_column: str, alias: str, level: CheckLevel
    ) -> pl.Expr:
        return (
            pl.when(pl.col(source_column) == self.value)
            .then(pl.lit(level))
            .otherwise(pl.lit(ROW_VALIDATION_SUCCESS_VALUE))
            .alias(alias)
        )


type ColumnCheckType = (
    IsValueEmpty | IsValueDuplicated | IsValueInvalidDate | IsValueEqualTo
)
