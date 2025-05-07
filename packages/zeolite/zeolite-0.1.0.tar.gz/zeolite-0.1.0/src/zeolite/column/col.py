from dataclasses import field
from typing import List, Any

from polars import Expr

from ._validation import ColumnCheckType
from ._utils.reference import ColumnRef
from ._validation.check_base import ThresholdType
from ._utils.col_base import ColumnSchema
from ._clean import CleanStage
from .._types import ColumnDataType, Sensitivity


# -----------------------------------------------------------------------------------------------------------
# Column Definitions
# -----------------------------------------------------------------------------------------------------------
def col(
    name: str,
    *,
    data_type: ColumnDataType = "unknown",
    sensitivity: Sensitivity = None,
    aliases: set[str] = None,
    validations: List[ColumnCheckType] = None,
    clean: CleanStage | ColumnDataType | dict[str, Any] | None = None,
) -> ColumnSchema:
    """
    Define a new column.

    Parameters:
        name: Name of the column.
        data_type: Data type of the column.
        sensitivity: Sensitivity of the column.
        aliases: Aliases for the column.
        validations: List of validation checks.
        clean: Clean stage for the column.

    Returns:
        ColumnSchema: The column schema.
    """
    return ColumnSchema(
        col_ref=ColumnRef(name),
        data_type=data_type,
        sensitivity=sensitivity,
        aliases=aliases,
        validations=validations,
        clean=clean,
    )


# -----------------------------------------------------------------------------------------------------------
# Data-Type Specific Column Definitions
# -----------------------------------------------------------------------------------------------------------


def str_col(
    name: str,
    *,
    sensitivity: Sensitivity = None,
    aliases: set[str] = None,
    validations: List[ColumnCheckType] = None,
    clean: CleanStage | ColumnDataType | dict[str, Any] | None = None,
) -> ColumnSchema:
    """
    Helper to define a new string column.
    """
    return col(
        name,
        data_type="string",
        sensitivity=sensitivity,
        aliases=aliases,
        validations=validations,
        clean=clean,
    )


def bool_col(
    name: str,
    *,
    sensitivity: Sensitivity = None,
    aliases: set[str] = None,
    validations: List[ColumnCheckType] = None,
    clean: CleanStage | ColumnDataType | dict[str, Any] | None = None,
) -> ColumnSchema:
    """
    Helper to define a new boolean column.
    """
    return col(
        name,
        data_type="boolean",
        sensitivity=sensitivity,
        aliases=aliases,
        validations=validations,
        clean=clean,
    )


def date_col(
    name: str,
    *,
    sensitivity: Sensitivity = None,
    aliases: set[str] = None,
    validations: List[ColumnCheckType] = None,
    clean: CleanStage | ColumnDataType | dict[str, Any] | None = None,
) -> ColumnSchema:
    """
    Helper to define a new date column.
    """
    return col(
        name,
        data_type="date",
        sensitivity=sensitivity,
        aliases=aliases,
        validations=validations,
        clean=clean,
    )


def int_col(
    name: str,
    *,
    sensitivity: Sensitivity = None,
    aliases: set[str] = None,
    validations: List[ColumnCheckType] = None,
    clean: CleanStage | ColumnDataType | dict[str, Any] | None = None,
) -> ColumnSchema:
    """
    Helper to define a new integer column.
    """
    return col(
        name,
        data_type="integer",
        sensitivity=sensitivity,
        aliases=aliases,
        validations=validations,
        clean=clean,
    )


def float_col(
    name: str,
    *,
    sensitivity: Sensitivity = None,
    aliases: set[str] = None,
    validations: List[ColumnCheckType] = None,
    clean: CleanStage | ColumnDataType | dict[str, Any] | None = None,
) -> ColumnSchema:
    """
    Helper to define a new float column.
    """
    return col(
        name,
        data_type="float",
        sensitivity=sensitivity,
        aliases=aliases,
        validations=validations,
        clean=clean,
    )


# -----------------------------------------------------------------------------------------------------------
# Derived Column Definitions
# -----------------------------------------------------------------------------------------------------------


def derived_col(
    name: str,
    *,
    function: Expr,
    data_type: ColumnDataType = "unknown",
    sensitivity: Sensitivity = None,
    validations: List[ColumnCheckType] = None,
    # clean: CleanStage | ColumnDataType | dict[str, Any] | None = None
) -> ColumnSchema:
    """
    Define a derived column whose value is computed from an expression.

    Parameters:
        name: Name of the derived column.
        function: Polars expression to compute the column.
        data_type: Data type of the column.
        sensitivity: Sensitivity of the column.
        validations: List of validation checks.

    Returns:
        ColumnSchema: The derived column schema.
    """
    return ColumnSchema(
        col_ref=ColumnRef(name).derived(),
        data_type=data_type,
        sensitivity=sensitivity,
        validations=validations,
    )._expression(function)


def derived_custom_check(
    name: str,
    *,
    function: Expr,
    sensitivity: Sensitivity = Sensitivity.NON_SENSITIVE,
    thresholds: ThresholdType = None,
    message: str = field(default=""),
) -> ColumnSchema:
    """
    Define a derived custom check/validation that is computed from an expression.

    Parameters:
        name: Name of the derived validation.
        function: Polars expression to compute the validation.
        sensitivity: Sensitivity of the validation.
        thresholds: Thresholds for the validation.
        message: Message for the validation.

    Returns:
        ColumnSchema: The derived validation schema.
    """
    return ColumnSchema(
        col_ref=ColumnRef(name).custom_check(),
        data_type="boolean",
        sensitivity=sensitivity,
    )._custom_validation(function, thresholds, message)


def meta_col(
    name: str,
    *,
    function: Expr = None,
    data_type: ColumnDataType = "unknown",
    sensitivity: Sensitivity = None,
) -> ColumnSchema:
    """
    Define a meta column - this is a special column that is usually added
    to the data e.g. during initial ingestion, and should be identified as
    separate from the source data.

    Parameters:
        name: Name of the meta column.
        function: Polars expression to compute the column.
        data_type: Data type of the column.
        sensitivity: Sensitivity of the column.

    Returns:
        ColumnSchema: The meta column schema.
    """
    col_schema = ColumnSchema(
        col_ref=ColumnRef(name, is_meta=True),
        data_type=data_type,
        sensitivity=sensitivity,
    )
    return col_schema._expression(function) if function else col_schema
