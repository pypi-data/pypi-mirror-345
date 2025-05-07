import polars as pl
from datetime import date


def calculate_age(
    col: str,
    *,
    comparison_date: date | str | pl.Expr = date.today(),
    alias: str = "age",
):
    if isinstance(comparison_date, date):
        return (
            pl.lit(comparison_date.year)
            - pl.col(col).dt.year()
            - (
                (pl.lit(comparison_date.month) < pl.col(col).dt.month())
                | (
                    (pl.lit(comparison_date.month) == pl.col(col).dt.month())
                    & (pl.lit(comparison_date.day) < pl.col(col).dt.day())
                )
            )
        ).alias(alias)

    elif isinstance(comparison_date, str):
        return (
            pl.col(comparison_date).dt.year()
            - pl.col(col).dt.year()
            - (
                (pl.col(comparison_date).dt.month() < pl.col(col).dt.month())
                | (
                    (pl.col(comparison_date).dt.month() == pl.col(col).dt.month())
                    & (pl.col(comparison_date).dt.day() < pl.col(col).dt.day())
                )
            )
        ).alias(alias)

    elif isinstance(comparison_date, pl.Expr):
        return (
            comparison_date.dt.year()
            - pl.col(col).dt.year()
            - (
                (comparison_date.dt.month() < pl.col(col).dt.month())
                | (
                    (comparison_date.dt.month() == pl.col(col).dt.month())
                    & (comparison_date.dt.day() < pl.col(col).dt.day())
                )
            )
        ).alias(alias)

    else:
        raise ValueError(f"Invalid comparison_date type: {type(comparison_date)}")
