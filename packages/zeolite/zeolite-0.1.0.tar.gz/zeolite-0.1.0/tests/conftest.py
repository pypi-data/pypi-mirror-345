import pytest
import polars as pl
from zeolite._types import ColumnNode, Sensitivity
from zeolite._types.validation.threshold import Threshold, ThresholdLevel


@pytest.fixture
def sample_df():
    """Sample DataFrame for testing"""
    return pl.DataFrame(
        {
            "string_col": ["value1", None, "", "value2"],
            "number_col": [1, 2, None, 4],
            "boolean_col": ["yes", "no", "true", "invalid"],
        }
    )


@pytest.fixture
def sample_threshold():
    """Sample threshold configuration"""
    return Threshold(
        warning=0.1,  # 10% threshold
        error=0.5,  # 50% threshold
        reject=0.8,  # 80% threshold
    )


@pytest.fixture
def sample_column_node():
    """Sample column node for testing"""
    return ColumnNode(
        id="test::sample",
        name="sample",
        data_type="string",
        column_type="source",
        sensitivity=Sensitivity.NON_SENSITIVE,
        schema="test",
        stage=None,
        expression=None,
        validation_rule=None,
    )


@pytest.fixture
def sample_error_levels():
    """Sample error levels for testing"""
    return {
        "warning": ThresholdLevel.WARNING.level,
        "error": ThresholdLevel.ERROR.level,
        "reject": ThresholdLevel.REJECT.level,
    }
