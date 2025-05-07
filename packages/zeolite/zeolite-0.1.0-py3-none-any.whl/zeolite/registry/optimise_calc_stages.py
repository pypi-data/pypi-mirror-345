from collections import defaultdict
from typing import List

from .._types import ColumnNode


# %%
def _extract_calculated_columns(columns: List[ColumnNode]) -> List[ColumnNode]:
    """
    Filter out columns with None expressions and clean up removed columns from dependencies
    """
    # Identify calculated columns
    columns_with_expr = {col.id for col in columns if col.expression is not None}

    # Remove non-calc columns and clean up calculated dependencies
    filtered_columns = []
    for col in columns:
        if col.expression is not None:
            # Clean up parent_ids to only reference calculated columns
            cleaned_col = col.with_parent_ids(
                src for src in col.parent_ids if src in columns_with_expr
            )
            filtered_columns.append(cleaned_col)

    return filtered_columns


# %%
def generate_optimized_stages(all_columns: List[ColumnNode]) -> List[List[ColumnNode]]:
    """
    Split columns into sequential stages based on their dependencies (using topological search!).
    Each stage contains complete column definitions that can be calculated once all columns
    in previous stages are available.
    """
    columns = _extract_calculated_columns(all_columns)

    # Create a map of column id to its definition for easy lookup
    column_map = {col.id: col for col in columns}

    # Create dependency graph and track in-degrees
    dependencies = defaultdict(set)
    in_degrees = defaultdict(int)

    # Build the dependency graph
    for col in columns:
        col_id = col.id
        for source in col.parent_ids:
            if (
                source in column_map
            ):  # Only count dependencies that exist in our column list
                dependencies[source].add(col_id)
                in_degrees[col_id] += 1

    # Initialize stages
    stages = []

    # Find all columns with no dependencies (in_degree = 0)
    zero_degree = [col.id for col in columns if in_degrees[col.id] == 0]

    while zero_degree:
        # Process current level
        current_stage = []
        next_zero_degree = []

        # Add all current zero-degree nodes to current stage
        for col_id in zero_degree:
            current_stage.append(column_map[col_id])

            # Reduce in_degree for all dependent columns
            for dependent in dependencies[col_id]:
                in_degrees[dependent] -= 1
                if in_degrees[dependent] == 0:
                    next_zero_degree.append(dependent)

        stages.append(current_stage)
        zero_degree = next_zero_degree

    # Check for circular dependencies
    remaining_columns = sum(1 for col in columns if in_degrees[col.id] > 0)
    if remaining_columns > 0:
        raise ValueError(
            f"Circular dependency detected! {remaining_columns} columns could not be processed."
        )

    return stages
