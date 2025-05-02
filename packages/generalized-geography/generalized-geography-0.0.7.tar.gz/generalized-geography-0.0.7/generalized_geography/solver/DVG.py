# Directed Vertex Geography


from typing import Dict
from networkx import DiGraph, descendants
from generalized_geography.common.constants import LOSE, WIN
from generalized_geography.common.types import NodeValue
from generalized_geography.solver.RDG import RDGSolver


class DVGSolver(RDGSolver):
    graph: DiGraph
    winlose: Dict[NodeValue, int]

    def __init__(self, graph: DiGraph):
        super().__init__(graph)
        self.fastly_classify()

    def fastly_classify(self, verbose=0):
        self.remove_loops(verbose=verbose)
        self.classify_repetitive_winlose(verbose=verbose)

    def remove_loops(self, verbose=0):
        if verbose == 1:
            print("Remove loops : ", end="")

        loop_nodes = [
            node for node in self.graph if self.graph.has_edge(node, node)]
        for node in loop_nodes:
            self.graph.remove_edge(node, node)

        if verbose == 1:
            print(f"{len(loop_nodes)} edge removed")

    def is_win_dfs(self, node):
        if node in self.winlose:
            return self.winlose[node] == WIN

        reachable_nodes = descendants(self.graph, node)
        subgraph: DiGraph = self.graph.subgraph(reachable_nodes)

        for succ in self.graph.successors(node):
            graph_copy = subgraph.copy()

            if not DVGSolver(graph_copy).is_win_dfs(succ):
                return True

        return False

    def completely_classify(self):
        new_winlose = {node: WIN if self.is_win_dfs(
            node) else LOSE for node in self.graph.nodes}
        self.winlose.update(new_winlose)


if __name__ == "__main__":
    g = DiGraph()
    g.add_edge(1, 2)
    g.add_edge(2, 3)
    g.add_edge(3, 1)
    g.add_edge(2, 4)
    g.add_edge(4, 5)
    solver = DVGSolver(g)
    print(solver.winlose)
    solver.completely_classify()
    print(solver.winlose)
