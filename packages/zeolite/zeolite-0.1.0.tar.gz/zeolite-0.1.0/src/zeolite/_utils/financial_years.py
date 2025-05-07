import polars as pl


def calc_financial_year_dates(date_col: str, *, prefix="") -> list[pl.Expr]:
    return [
        pl.col(date_col).dt.month().alias(f"{prefix}month"),
        pl.col(date_col).dt.to_string("%B").alias(f"{prefix}month_label"),
        pl.col(date_col).dt.year().alias(f"{prefix}calendar_year"),
        # ----------------------------------------------
        pl.when(pl.col(date_col).dt.quarter() > 2)
        .then(pl.col(date_col).dt.quarter() - 2)
        .otherwise(pl.col(date_col).dt.quarter() + 2)
        .alias(f"{prefix}financial_quarter"),
        # ----------------------------------------------
        pl.concat_str(
            [
                pl.col(date_col).dt.offset_by("-6mo").dt.year(),
                pl.col(date_col).dt.offset_by("6mo").dt.year(),
            ],
            separator="/",
        ).alias(f"{prefix}financial_year"),
        # ----------------------------------------------
        pl.col(date_col)
        .dt.month_start()
        .cast(pl.Date)
        .alias(f"{prefix}month_start_date"),
        pl.col(date_col).dt.month_end().cast(pl.Date).alias(f"{prefix}month_end_date"),
        pl.date(pl.col(date_col).dt.offset_by("-6mo").dt.year(), 7, 1).alias(
            f"{prefix}financial_year_start_date"
        ),
        pl.date(pl.col(date_col).dt.offset_by("6mo").dt.year(), 6, 30).alias(
            f"{prefix}financial_year_end_date"
        ),
        # fy_start=pl.when(pl.col("a").dt.quarter() > 2).then(pl.date(pl.col("a").dt.year(), 7, 1)).otherwise(
    ]
