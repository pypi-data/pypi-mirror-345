from collections import defaultdict

from .._types import ColumnNode


# %%
def verify_column_registry_integrity(columns: list[ColumnNode]) -> bool:
    """
    Verify column definitions by checking:
    1. All parent_columns reference existing column names
    2. All parent_ids match existing column IDs
    3. parent_ids are properly mapped from parent_columns

    Args:
        columns: List of column definitions

    Raises:
        ValueError: If validation fails, with detailed error message
    """
    # Create lookup maps
    column_by_id = {col.id: col for col in columns}
    column_by_name = {col.name: col for col in columns}

    # Check source references and mappings
    unmapped_sources = defaultdict(set)
    invalid_parent_ids = defaultdict(set)
    incorrect_mappings = defaultdict(set)

    for col in columns:
        # Check parent columns that don't map to any known column
        unmapped = {src for src in col.parent_columns if src not in column_by_name}
        if unmapped:
            unmapped_sources[col.id].update(unmapped)

        # Check parent_ids that don't exist
        invalid_ids = {
            src_id for src_id in col.parent_ids if src_id not in column_by_id
        }
        if invalid_ids:
            invalid_parent_ids[col.id].update(invalid_ids)

        # Check that all valid parent_columns are properly mapped to parent_ids
        for src in col.parent_columns:
            if src in column_by_name:
                expected_id = column_by_name[src].id
                if expected_id not in col.parent_ids:
                    incorrect_mappings[col.id].add(src)

    # Build error message if any issues found
    errors = []

    if unmapped_sources:
        error_details = "\n".join(
            f"Column '{col_id}' references non-existent columns: {sorted(refs)}"
            for col_id, refs in sorted(unmapped_sources.items())
        )
        errors.append(f"Unmapped source columns found:\n{error_details}")

    if invalid_parent_ids:
        error_details = "\n".join(
            f"Column '{col_id}' contains invalid source IDs: {sorted(refs)}"
            for col_id, refs in sorted(invalid_parent_ids.items())
        )
        errors.append(f"Invalid source IDs found:\n{error_details}")

    if incorrect_mappings:
        error_details = "\n".join(
            f"Column '{col_id}' has unmapped valid sources: {sorted(refs)}"
            for col_id, refs in sorted(incorrect_mappings.items())
        )
        errors.append(f"Incorrect source mappings found:\n{error_details}")

    if errors:
        raise ValueError("\n\n".join(errors))

    return True
