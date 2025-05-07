from enum import StrEnum, auto
import re
from typing import Dict, Literal

import polars as pl

from .._utils.column_id import extract_base_name

PREFIX = ""

"""
---------------------------------------------------------------------------------------------
    Cleaning functions
---------------------------------------------------------------------------------------------
These functions are used to clean the data in the columns - usually by converting to a 
correct data type
"""


class SanitiseLevel(StrEnum):
    FULL = auto()
    LOWERCASE = auto()
    TRIM = auto()


# Unfortunately, we can't use the enum as a type hint for the sanitise attribute
type SanitiseLevelType = Literal["full", "lowercase", "trim"] | None


def sanitise_string_col(
    col: str, *, sanitize_level: SanitiseLevelType = None, join_char: str = "_"
) -> pl.Expr:
    if sanitize_level == SanitiseLevel.FULL:
        return full_sanitise_string_col(col, join_char=join_char)
    elif sanitize_level == SanitiseLevel.LOWERCASE:
        return lower_sanitise_string_col(col)
    elif sanitize_level == SanitiseLevel.TRIM:
        return trim_sanitise_string_col(col)
    else:
        return pl.col(col)


def _sanitisation_fix(exp: pl.Expr, incorrect: str, corrected: str):
    # Can't do look behind regex in polars, so have to declare each option separately
    return (
        exp.str.replace_all(rf"^{incorrect}$", f"{corrected}", literal=False)
        .str.replace_all(rf"^{incorrect}_", f"{corrected}_", literal=False)
        .str.replace_all(rf"_{incorrect}$", f"_{corrected}", literal=False)
        .str.replace_all(rf"_{incorrect}_", f"_{corrected}_", literal=False)
    )


COMMON_MISTAKES = [
    ("m_ori", "maori"),
    ("wh_nau", "whanau"),
    ("i_d", "id"),
]


def trim_sanitise_string_col(col: str) -> pl.Expr:
    """
    Remove leading and trailing spaces
    """
    return pl.col(col).cast(pl.String).str.strip_chars()


def lower_sanitise_string_col(col: str) -> pl.Expr:
    """
    Convert to lowercase
    """
    return trim_sanitise_string_col(col).str.to_lowercase()


def full_sanitise_string_col(
    col: str,
    join_char="_",
) -> pl.Expr:
    new_col = (
        lower_sanitise_string_col(col)
        # Replace special characters with their plain letter counterparts
        .str.replace_all("ā", "a", literal=True)
        .str.replace_all("ē", "e", literal=True)
        .str.replace_all("ī", "i", literal=True)
        .str.replace_all("ō", "o", literal=True)
        .str.replace_all("ū", "u", literal=True)
        # Replace spaces, question marks, slashes, and line breaks with underscores
        .str.replace_all(r"[ ?/\n\r]", "_", literal=False)
        # Remove any non-alphanumeric characters (except underscores)
        .str.replace_all(r"[^a-z0-9_]", "_", literal=False)
    )
    # handle common mis-coded words
    for incorrect, corrected in COMMON_MISTAKES:
        new_col = _sanitisation_fix(new_col, incorrect, corrected)

    new_col = (
        new_col
        # Replace multiple underscores with a single one
        .str.replace_all(r"_+", "_", literal=False)
        # Strip leading and trailing spaces (technically underscores...)
        .str.strip_chars("_")
        # Change underscores back to spaces
        .str.replace_all("_", join_char, literal=True)
    )
    return new_col


def sanitise_scalar_string(value: str, join_char: str = "_") -> str:
    """
    Sanitise a string value by converting to lowercase, replacing special characters with their plain letter counterparts,
    and replacing spaces, question marks, slashes, and line breaks with underscores.
    Also handles common mis-coded words.
    """
    if not isinstance(value, str):
        value = str(value)

    value = (
        value.strip()
        .lower()
        .replace("ā", "a")
        .replace("ē", "e")
        .replace("ī", "i")
        .replace("ō", "o")
        .replace("ū", "u")
        .replace(" ", "_")
        .replace("?", "_")
        .replace("/", "_")
        .replace("\n", "_")
        .replace("\r", "_")
    )
    value = re.sub(r"[^a-z0-9_]", "_", value)

    for incorrect, corrected in COMMON_MISTAKES:
        value = re.sub(rf"^{incorrect}$", corrected, value)
        value = re.sub(rf"^{incorrect}_", f"{corrected}_", value)
        value = re.sub(rf"_{incorrect}$", f"_{corrected}", value)
        value = re.sub(rf"_{incorrect}_", f"_{corrected}_", value)

    return re.sub(r"_+", "_", value).strip("_").replace("_", join_char)


def clean_enum_col(
    col: str,
    enum_def=Dict[str, str],
    *,
    prefix: str = PREFIX,
    alias: str = None,
    default="No Data",
    sanitize: bool = True,
) -> pl.Expr:
    unique_values = set(enum_def.values())
    unique_values.add(default)
    new_col = pl.col(col) if not sanitize else full_sanitise_string_col(col)

    return new_col.replace(
        enum_def,
        default=default,
        return_dtype=pl.Enum(list(unique_values)),
    ).alias(alias if alias else f"{prefix}{col}")


def clean_boolean_col(
    col: str,
    *,
    prefix: str = PREFIX,
    alias: str = None,
    true_values=("yes", "true", "1"),
    false_values=("no", "false", "0"),
    sanitize: bool = True,
) -> pl.Expr:
    new_col = pl.col(col) if not sanitize else full_sanitise_string_col(col)

    return new_col.replace(
        {**{val: True for val in true_values}, **{val: False for val in false_values}},
        default=None,
        return_dtype=pl.Boolean,
    ).alias(alias if alias else f"{prefix}{col}")


def _col_sanitisation_fix(text, *, incorrect: str, corrected: str):
    pattern = rf"(?<![\w]){incorrect}(?![\w])|(?<=[\W_]){incorrect}(?=[\W_])|(?<=[\W_]){incorrect}(?=\b)|(?<=\b){incorrect}(?=[\W_])"
    return re.sub(pattern, corrected, text)


def sanitise_column_headers(lf: pl.LazyFrame, join_char="_") -> pl.LazyFrame:
    """
    --------------------------------------------------------------------------------------------------
      Sanitise column headers
    --------------------------------------------------------------------------------------------------
    This function takes a LazyFrame and sanitises the column headers by:

    - Lowercasing the column name
    - Replacing special characters with their plain letter counterparts
    - Replacing common incorrect words with their correct versions
    - Replacing spaces, dashes, question marks, slashes, and line breaks with underscores
    - Removing any non-alphanumeric characters (except underscores)
    - Replacing multiple underscores with a single one
    - Stripping leading and trailing underscores/spaces

    :param lf: The Polars LazyFrame to sanitise
    :param join_char: The character to use to join words in the column headers (default: "_")
    :return: A Polars LazyFrame with the column headers sanitised
    """

    def sanitise(column):
        name, prefix = extract_base_name(column)
        # Convert camel case to snake case, then lowercase
        col = re.sub(r"(?<!^)(?=[A-Z])", "_", column).lower()
        # Replace special characters with their plain letter counterparts
        for old, new in {"ā": "a", "ē": "e", "ī": "i", "ō": "o", "ū": "u"}.items():
            col = col.replace(old, new)

        # Replace spaces, question marks, slashes, and line breaks with underscores
        col = re.sub(r"[ ?/\n\r]", "_", col)
        # Replace any non-alphanumeric characters (except underscores)
        col = re.sub(r"[^a-z0-9_]", "_", col)

        # Handle common mis-coded words
        for incorrect, corrected in COMMON_MISTAKES:
            col = _col_sanitisation_fix(col, incorrect=incorrect, corrected=corrected)

        # Replace multiple underscores with a single one
        col = re.sub(r"_+", "_", col)
        # Strip leading and trailing underscores/spaces
        col = col.strip("_ ")

        return prefix + col.replace("_", join_char)

    return lf.rename(
        # {col: sanitise(col) for col in lf.collect_schema().names() if not re.match(_INTERNAL_COL_PATTERN, col)})
        {col: sanitise(col) for col in lf.collect_schema().names()}
    )
