from typing import Optional

from ._utils.reference import ColumnRef


# -----------------------------------------------------------------------------------------------------------
# Column References
# -----------------------------------------------------------------------------------------------------------
def ref(
    name: str,
    *,
    schema: Optional[str] = None,
    stage: Optional[str] = None,
    is_clean: bool = False,
    is_derived: bool = False,
    is_check: bool = False,
    is_meta: bool = False,
    is_custom_check: bool = False,
    check_name: str | None = None,
) -> ColumnRef:
    """
    Create a column reference for use in schema definitions.

    Parameters:
        name: Name of the column.

        is_clean: Whether the column is cleaned.
        is_derived: Whether the column is derived (calculated from other columns).
        is_check: Whether the column is a check/validation.
        is_meta: Whether the column is a meta column.
        is_custom_check: Whether the column is a custom check derived from an expression.
        check_name: Name of the check/validation.
        schema: Table schema name.
        stage: Pipeline stage name.

    Returns:
        ColumnRef: The column reference.
    """
    return ColumnRef(
        base_name=name,
        schema=schema,
        stage=stage,
        is_clean=is_clean,
        is_derived=is_derived,
        is_check=is_check,
        is_meta=is_meta,
        is_custom_check=is_custom_check,
        check_name=check_name,
    )


# -----------------------------------------------------------------------------------------------------------
# Column Reference Shortcuts
# -----------------------------------------------------------------------------------------------------------
def ref_meta(name: str) -> ColumnRef:
    """
    Create a column reference for a meta column.
    Parameters:
        name: Name of the column.

    Returns:
        ColumnRef: The column reference.
    """
    return ref(name=name, is_meta=True)


def ref_derived(name: str) -> ColumnRef:
    """
    Create a column reference to a derived column whose
    value is computed from an expression.

    Parameters:
        name: Name of the column.

    Returns:
        ColumnRef: The column reference.
    """
    return ref(name=name, is_derived=True)


def ref_custom_check(name: str) -> ColumnRef:
    """
    Create a column reference to derived custom check/validation
    (that is computed from an expression).

    Parameters:
        name: Name of the column.

    Returns:
        ColumnRef: The column reference.
    """
    return ref(name=name, is_custom_check=True, is_derived=True)
