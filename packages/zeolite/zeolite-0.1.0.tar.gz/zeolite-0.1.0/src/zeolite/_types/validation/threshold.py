# %%
from dataclasses import dataclass, field
from typing import Literal
from enum import Enum

# %%
type CheckThreshold = bool | int | float | Literal["any", "all"] | None

type CheckLevel = Literal["warning", "error", "reject", "pass"]


class ThresholdLevel(Enum):
    REJECT = ("reject", 3)
    ERROR = ("error", 2)
    WARNING = ("warning", 1)
    PASS = ("pass", 0)

    def __init__(self, level: CheckLevel, priority: int):
        self.level = level
        self.priority = priority


@dataclass(frozen=True)
class ThresholdResult:
    level: CheckLevel
    fraction_failed: float | None = None
    count_failed: int | None = None


def _parse_threshold_value(
    value: CheckThreshold, level_name: str
) -> tuple[float | None, int | None]:
    """Parse a threshold value into fraction and count components."""
    if value == 1 and value is not True:
        raise ValueError(
            f"`{level_name}` cannot be 1 as it is ambiguous, use `'all'` or `'any'` instead."
        )

    if value == "any" or value is True or value == 0:
        return 0, 1
    elif value == "all":
        return 1, None
    elif isinstance(value, (int, float)) and 0 < value < 1:
        return value, None
    elif isinstance(value, (int, float)) and value > 1:
        return None, round(value)
    elif isinstance(value, (int, float)) and value < 0:
        raise ValueError(f"Negative values are not allowed for `{level_name}`.")
    elif isinstance(value, str):
        if value not in ["any", "all"]:
            raise ValueError(
                f"`{level_name}` must be `'any'` or `'all'` for string values"
            )
        return (0, 1) if value == "any" else (1, None)
    return None, None


@dataclass()
class Threshold:
    warning: CheckThreshold = None
    error: CheckThreshold = None
    reject: CheckThreshold = None

    _thresholds: dict[ThresholdLevel, tuple[float | None, int | None]] = field(
        init=False
    )

    def __post_init__(self):
        if (self.warning is None) and (self.error is None) and (self.reject is None):
            raise ValueError(
                "At least one of `warning`, `error`, or `reject` must be provided"
            )

        # Initialize thresholds dictionary with parsed values
        thresholds = {}
        for level in [
            ThresholdLevel.REJECT,
            ThresholdLevel.ERROR,
            ThresholdLevel.WARNING,
        ]:
            value = getattr(self, level.level)
            if value is not None and value is not False:
                fraction, count = _parse_threshold_value(value, level.level)
                thresholds[level] = (fraction, count)

        object.__setattr__(self, "_thresholds", thresholds)

    def resolve(self, failed_rows: int, total_rows: int) -> ThresholdResult:
        """Resolve the threshold level based on failed rows and total rows."""
        if total_rows == 0:
            return ThresholdResult(level="pass")

        fraction_failed = failed_rows / total_rows if total_rows > 0 else 1
        rows_failed = failed_rows if failed_rows > 0 else 0

        # Check each threshold level in priority order
        for level in sorted(ThresholdLevel, key=lambda x: x.priority, reverse=True):
            if level == ThresholdLevel.PASS:
                continue

            fraction, count = self._thresholds.get(level, (None, None))

            # Check if threshold is met
            if (fraction is not None and fraction_failed >= fraction) or (
                count is not None and rows_failed >= count
            ):
                return ThresholdResult(
                    level=level.level,
                    fraction_failed=fraction_failed,
                    count_failed=rows_failed,
                )

        return ThresholdResult(
            level="pass", fraction_failed=fraction_failed, count_failed=rows_failed
        )
