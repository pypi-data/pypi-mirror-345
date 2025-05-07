from .schema import TableSchema
from .column.col import (
    col,
    str_col,
    bool_col,
    date_col,
    int_col,
    float_col,
    derived_col,
    derived_custom_check,
    meta_col,
)
from .column.ref import (
    ref,
    ref_meta,
    ref_derived,
    ref_custom_check,
)
from .column.checks import (
    check_is_value_empty,
    check_is_value_duplicated,
    check_is_value_invalid_date,
    check_is_value_equal_to,
)

from ._types.sensitivity import Sensitivity
from ._types.validation.threshold import Threshold

__all__ = [
    "schema",
    "col",
    "str_col",
    "bool_col",
    "date_col",
    "int_col",
    "float_col",
    "derived_col",
    "derived_custom_check",
    "meta_col",
    "check_is_value_empty",
    "check_is_value_duplicated",
    "check_is_value_invalid_date",
    "check_is_value_equal_to",
    "ref",
    "ref_meta",
    "ref_derived",
    "ref_custom_check",
    "Sensitivity",
    "Threshold",
]

schema: type[TableSchema] = TableSchema
"""
Create a new table schema.

Example:
    table = zeolite.schema("demo").columns([...])
"""

col = col
"""
Define a new column schema.

Example:
    zeolite.col("id").validations(zeolite.check_is_value_empty(), ...)
"""

str_col = str_col
"""
Helper to define a new string column.
"""

bool_col = bool_col
"""
Helper to define a new boolean column.
"""

date_col = date_col
"""
Helper to define a new date column.
"""

int_col = int_col
"""
Helper to define a new integer column.
"""

float_col = float_col
"""
Helper to define a new float column.
"""

derived_col = derived_col
"""
Define a derived column schema.

Example:
    zeolite.derived_col("id", function=zeolite.ref("other_column") + 1)
"""

derived_custom_check = derived_custom_check
"""
Define a derived validation.

Example:
    zeolite.derived_validation("id", function=zeolite.ref("other_column") + 1)
"""

meta_col = meta_col
"""
Define a meta column schema.

Example:
    zeolite.meta_col("id", function=zeolite.ref("other_column") + 1)
"""

check_is_value_empty = check_is_value_empty
"""
Validation: Check if a column value is empty/null.
"""

check_is_value_duplicated = check_is_value_duplicated
"""
Validation: Check if a column value is duplicated.
"""

check_is_value_invalid_date = check_is_value_invalid_date
"""
Validation: Check if a column value is an invalid date.
"""

check_is_value_equal_to = check_is_value_equal_to
"""
Validation: Check if a column value is equal to a specified value.
"""

ref = ref
"""
Create a column reference for use in schema definitions.

Example:
    zeolite.ref("other_column")
"""

ref_meta = ref_meta
"""
Create a meta column reference for use in schema definitions.

Example:
    zeolite.ref_meta("other_column")
"""

ref_derived = ref_derived
"""
Create a derived column reference for use in schema definitions.

Example:
    zeolite.ref_derived("other_column")
"""

ref_custom_check = ref_custom_check
"""
Create a custom check reference for use in schema definitions.

Example:
    zeolite.ref_custom_check("other_column")
"""

Sensitivity = Sensitivity
"""
Sensitivity type. Useful for attaching sensitivity labels to columns.
"""

Threshold = Threshold
"""
Threshold used for setting validation thresholds on column checks.
"""
