from typing import TYPE_CHECKING

from ..._types import ColumnNode
from ..._types.sensitivity import Sensitivity
from ..._types.validation.threshold import Threshold, ThresholdLevel, CheckLevel
from ..._types.validation.validation_rule import ColumnValidationRule

if TYPE_CHECKING:
    from .check_base import RowCheckBase
    from .._utils.reference import ColumnRef


def create_validation_rule(
    check_method_id: str,
    message: str,
    *,
    source_column: str,
    alias: str,
    schema: str,
    thresholds: Threshold | None,
) -> ColumnValidationRule | None:
    """Create a validation rule for a check"""
    if not thresholds:
        return None

    return ColumnValidationRule(
        check_id=check_method_id,
        message=message,
        thresholds=thresholds,
        source_column=source_column,
        check_column=alias,
        schema=schema,
    )


def _get_threshold_level(thresholds: Threshold | None) -> CheckLevel:
    # We default to WARNING if no thresholds are provided (otherwise you can't differentiate between a pass and a fail)
    if thresholds is None:
        return ThresholdLevel.WARNING.level

    res = thresholds.resolve(1, 1)

    if res.level == ThresholdLevel.PASS.level:
        return ThresholdLevel.WARNING.level

    return res.level


def get_validation_node(
    check: "RowCheckBase",
    *,
    source_column: "ColumnRef",
    thresholds: Threshold | None,
    check_on_cleaned: bool = False,
    alias: str | None = None,
    label: str | None = None,
) -> ColumnNode:
    """Create a validation node for a check"""
    label = label if label else check.method_id()
    _ref = source_column.clean() if check_on_cleaned else source_column

    alias = alias if alias else _ref.check(label).name

    assert alias != source_column.name, (
        f"Check column name must be different from column - {source_column.name}"
    )
    assert alias != _ref.name, (
        f"Check column name must be different from cleaned column - {_ref.name}"
    )

    expr = check._check_expression(
        _ref.name, alias, level=_get_threshold_level(thresholds)
    )
    validation_rule = create_validation_rule(
        check_method_id=check.method_id(),
        message=check.message,
        source_column=source_column.name,
        alias=alias,
        schema=source_column.schema,
        thresholds=thresholds,
    )

    return ColumnNode(
        id=_ref.check(label).id,
        name=alias,
        data_type="boolean",
        column_type="validation",
        schema=source_column.schema,
        stage=source_column.stage,
        sensitivity=Sensitivity.NON_SENSITIVE,
        expression=expr,
        validation_rule=validation_rule,
    )
