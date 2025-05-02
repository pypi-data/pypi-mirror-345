### Changeable Directed Edge Geography ###
# data structure : CDEGGraph that have nodes = V x {0,1} for some V and edges such that e[0][1] != e[1][1]
#                  노드는 (v,0) 또는 (v,1) 튜플로 나타내어짐
#                  엣지는 (u,0)->(v,1) 또는 (u,1)->(v,0) 꼴
# position : (G, (v, 0))


from typing import Dict, List
from networkx import DiGraph, condensation, descendants, strongly_connected_components
from generalized_geography.app.change_rules import std
from generalized_geography.app.rule import Rule
from generalized_geography.app.word_dict import WordDict
from generalized_geography.common.CDEG_graph import BipartiteNode, CDEGGraph, Move
from generalized_geography.common.constants import LOSE, WIN
from generalized_geography.common.types import NodeValue


class CDEGSolver:
    graph: CDEGGraph
    winlose: Dict[BipartiteNode, int]
    strategy: Dict[BipartiteNode, NodeValue]
    loops = DiGraph

    def __init__(self, graph: CDEGGraph):
        self.winlose = {}
        self.graph = graph
        self.strategy = {}
        self.loops = DiGraph()
        self.fastly_classify(verbose=0)

    def fastly_classify(self, verbose=0):
        self.classify_repetitive_winlose(verbose=verbose)
        self.remove_2_circuits(verbose=verbose)
        self.classify_loop_winlose(verbose=verbose)

    def classify_repetitive_winlose(self, verbose=0):
        if verbose == 1:
            print("Classify loop winlose : ", end="")

        sinks: List[BipartiteNode] = [node for node,
                                      deg in self.graph.out_degree() if deg == 0]

        for sink in sinks:
            self.winlose[sink] = LOSE

        while sinks:
            node = sinks.pop()
            preds = [pred for pred in self.graph.predecessors(node)
                     if pred not in self.winlose]

            self.graph.remove_node(node)

            if node.index == 0:
                if self.winlose[node] == LOSE:
                    for pred in preds:
                        self.strategy[pred] = node.value
                        self.winlose[pred] = WIN
                        sinks.append(pred)

                else:
                    for pred in preds:
                        if self.graph.out_degree(pred) == 0:
                            self.winlose[pred] = LOSE
                            sinks.append(pred)

            else:
                if self.winlose[node] == LOSE:
                    for pred in preds:
                        if self.graph.out_degree(pred) == 0:
                            self.strategy[pred] = node.value
                            self.winlose[pred] = LOSE
                            sinks.append(pred)

                else:
                    for pred in preds:
                        self.strategy[pred] = node.value
                        self.winlose[pred] = WIN
                        sinks.append(pred)

        if verbose == 1:
            win_nodes = [
                node for node in self.winlose if self.winlose[node] == WIN]
            lose_nodes = [
                node for node in self.winlose if self.winlose[node] == LOSE]
            print(len(win_nodes), "win,", len(lose_nodes),
                  "lose,", len(self.graph), "remain")

    def remove_2_circuits(self, unique_out_edges=None, verbose=0):

        if verbose == 1:
            print("Remove 2 cycles : ", end="")

        if unique_out_edges == None:
            unique_out_edges = self.graph.get_unique_out_edges()

        to_remove = []

        # self loop 짝수 개 검출
        for edge in unique_out_edges:
            m = self.graph.get_num(edge[1], edge[0])
            if m >= 2:
                to_remove.append((edge[1], edge[0], m - m % 2))

        # 2-cycle 검출
        for edge1 in unique_out_edges:
            for edge2 in unique_out_edges:
                if edge1 >= edge2:
                    continue
                if self.graph.has_edge(edge1[1], edge2[0]) and self.graph.has_edge(edge2[1], edge1[0]):
                    delete_num = min(
                        self.graph.get_num(edge1[1], edge2[0]),
                        self.graph.get_num(edge2[1], edge1[0])
                    )

                    to_remove.append((edge1[1], edge2[0], delete_num))
                    to_remove.append((edge2[1], edge1[0], delete_num))

        self.graph.decrease_edges_from(to_remove)

        if verbose == 1:
            print(sum([m for _, _, m in to_remove]), "edges removed")

    def classify_loop_winlose(self, unique_out_edges=None, verbose=0, lose_sinks=None, win_sinks=None):
        if verbose == 1:
            print("Classify loop winlose : ", end="")

        if unique_out_edges == None:
            unique_out_edges = self.graph.get_unique_out_edges()

        self.loops.clear()
        self.loops.add_edges_from(
            [(v, u) for u, v in unique_out_edges if self.graph.has_edge(v, u)])

        if not lose_sinks:
            lose_sinks = [node for node, deg in self.graph.out_degree()
                          if node.index == 1 and deg == 0]

        if not win_sinks:
            win_sinks = [node for node, deg in self.graph.out_degree(
            ) if node.index == 1 and deg == 1 and self.loops.has_edge(*list(self.graph.out_edges(node))[0])]

        for n in lose_sinks:
            self.winlose[n] = LOSE
        for n in win_sinks:
            self.strategy[n] = list(self.graph.out_edges(n))[0][1].value
            self.winlose[n] = WIN

        sinks: List[BipartiteNode] = win_sinks + lose_sinks

        while sinks:
            node = sinks.pop()

            preds = [pred for pred in self.graph.predecessors(
                node) if pred not in self.winlose]

            self.graph.remove_node(node)

            if node.index == 0:
                if self.winlose[node] == LOSE:
                    for pred in preds:
                        self.winlose[pred] = WIN
                        self.strategy[pred] = node.value
                        sinks.append(pred)

                else:
                    for pred in preds:
                        if self.graph.out_degree(pred) == 0:
                            self.winlose[pred] = LOSE
                            sinks.append(pred)

                        elif self.graph.out_degree(pred) == 1 and self.loops.has_edge(*list(self.graph.out_edges(pred))[0]):
                            self.winlose[pred] = WIN

                            self.strategy[pred] = list(
                                self.graph.out_edges(pred))[0][1].value
                            sinks.append(pred)
            else:
                if self.winlose[node] == LOSE:
                    for pred in preds:
                        if self.graph.out_degree(pred) == 0:
                            self.winlose[pred] = LOSE
                            sinks.append(pred)

                else:
                    for pred in preds:
                        self.winlose[pred] = WIN
                        self.strategy[pred] = node.value
                        sinks.append(pred)

        if verbose == 1:
            win_nodes = [
                node for node in self.winlose if self.winlose[node] == WIN]
            lose_nodes = [
                node for node in self.winlose if self.winlose[node] == LOSE]
            print(len(win_nodes), "win,", len(lose_nodes),
                  "lose,", len(self.graph), "remain")

    # def copy(self):
    #     cdeg = CDEG(self.graph.copy())
    #     cdeg.winlose = self.winlose.copy()
    #     cdeg.strategy = self.strategy.copy()
    #     cdeg.two_cycles = self.two_cycles.copy()
    #     cdeg.loops = self.loops.copy()
    #     return cdeg

    # def is_win(self, node: any, sorted_func=None, win_callback=None, cnt_limit=None):

    #     def dfs(graph: CDEGGraph, node: any, trail: Optional[Move] = None):

    #         nonlocal cnt_limit
    #         nonlocal sorted_func

    #         if cnt_limit != None and cnt_limit == 0:
    #             raise ExceedLimitError

    #         if trail == None:
    #             trail = []

    #         graph_copy = reachable_graph(graph, node)

    #         cdeg = CDEG(graph_copy)
    #         cdeg.fastly_classify()

    #         winlose = cdeg.winlose

    #         if (node, 0) in winlose:
    #             if winlose[(node, 0)] == WIN:
    #                 return true
    #             else:
    #                 if win_callback:
    #                     win_callback(trail)
    #                 if cnt_limit:
    #                     cnt_limit -= 1
    #                 return false

    #         # print(graph_copy.edges)
    #         edges = moves(graph_copy, node)
    #         edges = sorted(edges, key=lambda x: len(
    #             moves(graph_copy, x[-1])))
    #         if sorted_func:
    #             edges = sorted_func(edges, trail)

    #         for edge in edges:
    #             graph_copy.remove_edge(BipartiteNode(
    #                 edge[0], 1), BipartiteNode(edge[1], 0), 1)
    #             if not dfs(graph_copy, edge[-1], [*trail, (edge[0], edge[1])]):
    #                 return True
    #             graph_copy.add_edge(BipartiteNode(
    #                 edge[0], 1), BipartiteNode(edge[1], 0), 1)

    #         win_callback(trail)
    #         if cnt_limit:
    #             cnt_limit -= 1
    #         return False

    #     return dfs(self.graph, node)


def reachable_graph(graph: CDEGGraph, node: any) -> CDEGGraph:
    if type(node) != BipartiteNode:
        node = BipartiteNode(node, 0)
    reachable_nodes = descendants(graph, node) | {node}
    subgraph = graph.subgraph(reachable_nodes).copy()
    return subgraph


def get_major_graph(graph: CDEGGraph) -> CDEGGraph:
    scc_list = list(strongly_connected_components(graph))
    scc_graph = condensation(graph, scc_list)
    leaf_scc_indices = {
        n for n in scc_graph if scc_graph.out_degree(n) == 0}
    leaf_sccs = [scc_list[i] for i in leaf_scc_indices]

    if len(leaf_sccs) != 1:
        raise Exception("주요 루트 없음")

    return graph.subgraph(leaf_sccs[0]).copy()


def moves(graph: CDEGGraph, node: any) -> List[Move]:

    return [(succ0.value, succ1.value)
            for succ0 in graph.successors(BipartiteNode(node, 0))
            for succ1 in graph.successors(succ0)]


if __name__ == "__main__":

    with open("dataset/oldict.txt", "r", encoding="UTF-8") as f:
        words = [word.strip() for word in f.read().split("\n")]
    rule = Rule(0, -1, std)
    word_dict = WordDict(rule, words)
    graph = word_dict.make_graph()
    solver = CDEGSolver(graph)
