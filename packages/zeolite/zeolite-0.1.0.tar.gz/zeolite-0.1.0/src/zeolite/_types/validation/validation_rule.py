from dataclasses import KW_ONLY, dataclass
import polars as pl

from .threshold import Threshold, ThresholdLevel
from ..error import DataValidationError

type CheckValue = (
    str
    | int
    | float
    | bool
    | None
    | list[str]
    | list[int]
    | list[float]
    | list[bool]
    | set[str]
    | set[int]
    | set[float]
    | set[bool]
)


@dataclass(frozen=True)
class ColumnValidationRule:
    check_id: str
    _: KW_ONLY
    thresholds: Threshold
    message: str
    source_column: str
    check_column: str
    schema: str

    def validate(self, lf: pl.LazyFrame) -> DataValidationError | None:
        checks = lf.select(
            pl.len().alias("total_rows"),
            pl.col(self.check_column)
            .ne(ThresholdLevel.PASS.level)
            .sum()
            .alias("failed_rows"),
        ).collect()

        total_rows = checks["total_rows"].item()
        failed_rows = checks["failed_rows"].item()

        if failed_rows == 0:
            return None

        res = self.thresholds.resolve(failed_rows=failed_rows, total_rows=total_rows)

        return (
            DataValidationError(
                schema=self.schema,
                column=self.check_column,
                error=self.check_id,
                level=res.level,
                fraction_failed=res.fraction_failed,
                count_failed=res.count_failed,
                message=self._format_message(
                    self.source_column, failed_rows, total_rows
                ),
            )
            if res.level != "pass"
            else None
        )

    def _format_message(
        self,
        col: str,
        count: int,
        total: int,
        value: str | int | float | bool | None = None,
    ) -> str:
        return (
            self.message.replace("{{column}}", f"'{col}'")
            .replace("{{count}}", f"{count:,}")
            .replace("{{fraction}}", f"{count / total:,.2%}")
        )
