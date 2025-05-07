import json
from datetime import datetime
from enum import StrEnum
from typing import Any, List
import polars as pl

from .._types import ColumnNode
from .._types.graph import Graph
from .lineage import create_dependency_graph
from .optimise_calc_stages import generate_optimized_stages
from .verify_registry import verify_column_registry_integrity


# %%
class ColumnRegistry:
    def __init__(self, columns: list[ColumnNode] = None):
        self.by_id: dict[str, ColumnNode] = {}
        self.by_name: dict[str, ColumnNode] = {}

        cols = columns if columns is not None else []
        self.extend(cols)

    # ---------------------------------------------------------------------------------
    # Registry setup/management
    # ---------------------------------------------------------------------------------
    def append(self, column: ColumnNode) -> None:
        self._append(column)
        self._post_update()

    def extend(self, columns: list[ColumnNode]) -> None:
        for c in columns:
            self._append(c)
        self._post_update()

    def get_by_id(self, id: str) -> ColumnNode | None:
        return self.by_id.get(id)

    def get_by_name(self, name: str) -> ColumnNode | None:
        return self.by_name.get(name)

    def remove(self, column: ColumnNode) -> None:
        self.by_id.pop(column.id, None)
        self.by_name.pop(column.name, None)

    def get_all_ids(self):
        return self.by_id.keys()

    def _append(self, column: ColumnNode) -> None:
        assert column.id not in self.by_id, f"Duplicate column ID: {column.id}"
        assert column.name not in self.by_name, f"Duplicate column name: {column.name}"
        self.by_id[column.id] = column
        self.by_name[column.name] = column

    def _replace(self, column: ColumnNode) -> None:
        self.by_id[column.id] = column
        self.by_name[column.name] = column

    def _post_update(self) -> None:
        """
        When columns have been added to the registry, this method
        maps the parent_column names to the actual column/node IDs.
        """

        for col in self.nodes():
            if len(col.parent_columns) > 0:
                # self._replace(col.with_parent_ids({self.by_name[source].id if source in self.by_name else source for source in col.parent_columns}))

                # Only include source IDs for columns that exist in the registry
                matched_parent_ids = {
                    self.by_name[source].id
                    for source in col.parent_columns
                    if source in self.by_name
                }
                self._replace(col.with_parent_ids(matched_parent_ids))

    # ---------------------------------------------------------------------------------
    # Special methods
    # ---------------------------------------------------------------------------------
    def lineage(self) -> Graph:
        dependency_graph = create_dependency_graph(self.nodes())

        # return json.dumps(dependency_graph, cls=_SchemaJsonEncoder)
        return dependency_graph

    def verify_integrity(self) -> bool:
        return verify_column_registry_integrity(self.nodes())

    def get_execution_stages(self) -> List[List[ColumnNode]]:
        return generate_optimized_stages(self.nodes())

    # ----------------------------------------------------------------------------------
    #  Iterator methods
    # ----------------------------------------------------------------------------------
    def nodes(self) -> list[ColumnNode]:
        return list(self.by_id.values())

    def __iter__(self):
        return iter(self.nodes())


class _SchemaJsonEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, StrEnum):
            return obj.value
        if isinstance(obj, set):
            return list(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, pl.Expr):
            return str(obj)
        if isinstance(obj, ColumnRegistry):
            return obj.by_name

        # if isinstance(obj, Graph):
        #     return asdict(obj)

        # if isinstance(obj, DerivedColumns):
        #     cols = [c.meta.output_name() for c in obj.args]
        #     cols.extend([k for k in obj.kwargs.keys()])
        #     return cols
        return super().default(obj)
