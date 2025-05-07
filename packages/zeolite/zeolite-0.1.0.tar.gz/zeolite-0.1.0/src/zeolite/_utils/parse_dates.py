import polars as pl
from datetime import datetime, timezone

tz = "UTC"


def mega_date_handler(
    col: str, alias: str = "parsed_date", output_format: pl.Date | pl.Datetime = pl.Date
):
    # Cast to string to avoid type errors
    date_col = pl.col(col).cast(pl.String)

    return (
        # ----------------------------------------------------------------------
        # ISO datetime e.g. 2024-01-25T00:00:00Z
        pl.when(
            date_col.str.contains(
                r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})?$"
            )
        )
        .then(
            date_col.str.replace("Z", "+00:00").str.to_datetime(
                "%FT%T%.f%z", strict=False, time_zone=tz
            )
        )
        # ----------------------------------------------------------------------
        # Compressed ISO datetime e.g. 20240125T000000Z
        .when(date_col.str.contains(r"^\d{8}T\d{6}Z$"))
        .then(
            date_col.str.replace_all(r"Z|T", "").str.to_datetime(
                "%Y%m%d%H%M%S", strict=False, time_zone=tz
            )
        )
        # ----------------------------------------------------------------------
        # Weird ISO datetime e.g. 2024-01-25 00:00:00
        .when(date_col.str.contains(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\d*$"))
        .then(
            date_col.str.slice(0, 19).str.to_datetime(
                "%Y-%m-%d %H:%M:%S", strict=False, time_zone=tz
            )
        )
        # ----------------------------------------------------------------------
        # ISO date e.g. 2024-01-25
        .when(date_col.str.contains(r"^\d{4}-\d{2}-\d{2}$"))
        .then(date_col.str.to_datetime("%Y-%m-%d", strict=False, time_zone=tz))
        # ----------------------------------------------------------------------
        # NZ date e.g. 25/01/2024
        .when(date_col.str.contains(r"^\d{1,2}/\d{1,2}/\d{4}$"))
        .then(date_col.str.to_datetime("%d/%m/%Y", strict=False, time_zone=tz))
        # ----------------------------------------------------------------------
        # NZ datetime e.g. 25/01/2024 00:00
        .when(date_col.str.contains(r"^\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d{2}$"))
        .then(date_col.str.to_datetime("%d/%m/%Y %k:%M", strict=False, time_zone=tz))
        # ----------------------------------------------------------------------
        # NZ datetime extended e.g. 25/01/2024 12:00:00am
        .when(
            date_col.str.contains(
                r"^\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d{2}:\d{2}\s(?:am|pm|AM|PM)"
            )
        )
        .then(date_col.str.to_datetime("%d/%m/%Y %r", strict=False, time_zone=tz))
        # ----------------------------------------------------------------------
        # Weird NZ date e.g. 25.01.2024
        .when(date_col.str.contains(r"^\d{1,2}\.\d{1,2}\.\d{4}$"))
        .then(date_col.str.to_datetime("%d.%m.%Y", strict=False, time_zone=tz))
        # ----------------------------------------------------------------------
        # Even weirder NZ date e.g. 25 01 2024
        .when(date_col.str.contains(r"^\d{1,2} \d{1,2} \d{4}$"))
        .then(date_col.str.to_datetime("%d %m %Y", strict=False, time_zone=tz))
        # ----------------------------------------------------------------------
        # Unix timestamp e.g. 1716720000
        .when(date_col.str.contains(r"^\d{8,16}$"))
        .then(
            date_col.str.slice(0, 10).str.to_datetime("%s", strict=False, time_zone=tz)
        )
        # ----------------------------------------------------------------------
        # Excel date handling
        .when(date_col.str.contains(r"^\d{1,6}(\.\d+)?$"))
        .then(
            pl.lit(datetime(1899, 12, 30, tzinfo=timezone.utc))
            + pl.duration(minutes=(pl.col(col).cast(pl.Float64, strict=False) * 1440))
        )
        # ----------------------------------------------------------------------
        .otherwise(pl.lit(None))
        .alias(alias)
        .cast(output_format)
    )
