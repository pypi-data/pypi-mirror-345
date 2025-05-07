from typing import Literal

type ColumnDataType = Literal[
    "string",
    "id",
    "number",
    "integer",
    "float",
    "boolean",
    "date",
    "datetime",
    "enum",
    "sanitised_string",
    "unknown",
]
