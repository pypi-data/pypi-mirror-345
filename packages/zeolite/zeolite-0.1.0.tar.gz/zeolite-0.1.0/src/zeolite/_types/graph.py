from typing import TypedDict, List


class Node(TypedDict):
    id: str
    name: str
    type: str
    schema: str
    stage: str
    validation_level: str | None
    node_category: str
    sensitivity: str


class Edge(TypedDict):
    source: str
    target: str


class Graph(TypedDict):
    nodes: List[Node]
    edges: List[Edge]
