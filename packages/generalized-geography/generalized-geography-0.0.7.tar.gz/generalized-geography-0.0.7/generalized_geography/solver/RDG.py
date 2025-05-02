# Directed Edge/Vertex Geography with Repetitions

from typing import Dict
from networkx import DiGraph
from generalized_geography.common.constants import LOSE, WIN
from generalized_geography.common.types import NodeValue


class RDGSolver:
    graph: DiGraph
    winlose: Dict[NodeValue, int]

    def __init__(self, graph: DiGraph):
        self.graph = graph
        self.winlose = {}

    def classify_repetitive_winlose(self, sinks=None, verbose=0):
        if verbose == 1:
            print("Classify repetitive winlose : ", end="")

        if not sinks:
            sinks = [node for node, deg in self.graph.out_degree() if deg == 0]

        for n in sinks:
            self.winlose[n] = LOSE

        while sinks:
            node = sinks.pop()
            preds = [pred for pred in self.graph.predecessors(
                node) if pred not in self.winlose]
            self.graph.remove_node(node)
            if self.winlose[node] == LOSE:
                for pred in preds:
                    self.winlose[pred] = WIN
                    sinks.append(pred)
            else:
                for pred in preds:
                    if self.graph.out_degree(pred) == 0:
                        self.winlose[pred] = LOSE
                        sinks.append(pred)

        if verbose == 1:
            win_nodes = [
                node for node in self.winlose if self.winlose[node] == WIN]
            lose_nodes = [
                node for node in self.winlose if self.winlose[node] == LOSE]
            print(len(win_nodes), "win,", len(lose_nodes),
                  "lose,", len(self.graph), "remain")
