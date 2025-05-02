#

from typing import NamedTuple, NewType, Tuple, TypeVar
from generalized_geography.common.types import NodeValue
from generalized_geography.common.unlabeled_multidigraph import UnlabeledMultiDiGraph


class BipartiteNode(NamedTuple):
    value: NodeValue
    index: int

    def __str__(self):
        return f"{self.value}{self.index}"

    def __repr__(self):
        return f"{self.value}{self.index}"


BipartiteEdge = NewType("BipartiteEdge", Tuple[BipartiteNode, BipartiteNode])
Move = NewType("Move", Tuple[NodeValue, NodeValue])


class CDEGGraph(UnlabeledMultiDiGraph):
    def __init__(self):
        super().__init__()

    def get_0_nodes(self):
        return [node for node in self.nodes if node.index == 0]

    def get_1_nodes(self):
        return [node for node in self.nodes if node.index == 1]

    def get_01_edges(self):
        return [edge for edge in self.edges if edge[0].index == 0]

    def get_10_edges(self):
        return [edge for edge in self.edges if edge[0].index == 1]

    def get_unique_out_edges(self):
        nodes = [node for node, deg in self.out_degree() if node.index ==
                 0 and deg == 1]
        edges = [list(self.out_edges(node))[0] for node in nodes]
        return edges
