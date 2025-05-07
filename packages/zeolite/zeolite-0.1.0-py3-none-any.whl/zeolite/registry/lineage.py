from typing import List

from .._types import ColumnNode
from .._types.graph import Node, Edge, Graph


def create_dependency_graph(columns: list[ColumnNode]) -> Graph:
    """
    Convert column definitions into a graph structure with nodes and edges.
    """
    nodes: List[Node] = [
        Node(
            id=col.id,
            name=col.name,
            type=col.data_type,
            sensitivity=col.sensitivity,
            schema=col.schema,
            stage=col.stage,
            node_category="column",
        )
        for col in columns
    ]

    edges: List[Edge] = [
        Edge(source=source, target=col.id)
        for col in columns
        for source in col.parent_ids
    ]

    return Graph(nodes=nodes, edges=edges)
