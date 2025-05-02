# 엣지 (u, v)의 개수를 "num" attribute로 표현한 MultiDiGraph

from networkx import MultiDiGraph
from networkx.classes.digraph import DiGraph
from networkx.exception import NetworkXError


class UnlabeledMultiDiGraph(DiGraph):
    @classmethod
    def from_nx_graph(self, mdg: DiGraph | MultiDiGraph):
        c = self()
        c.add_nodes_from(mdg.nodes())
        c.increase_edges_from(mdg.edges())
        return c

    def edge_dict(self):
        return {"num": 1}

    edge_attr_dict_factory = edge_dict

    def __init__(self):
        super().__init__()

    def increase_edge(self, u, v, num=1):
        if self.has_edge(u, v):
            self[u][v]['num'] += num
        else:
            super().add_edge(u, v, num=num)

    def increase_edges_from(self, ebunch_to_add):
        for e in ebunch_to_add:
            ne = len(e)
            if ne == 3:
                u, v, num = e
            elif ne == 2:
                u, v = e
                num = 1
            else:
                raise NetworkXError("")
            self.increase_edge(u, v, num)

    def decrease_edge(self, u, v, num=1):
        if self.has_edge(u, v):
            if self[u][v]['num'] > num:
                self[u][v]['num'] -= num
            else:
                super().remove_edge(u, v)

    def decrease_edges_from(self, ebunch):
        for e in ebunch:
            ne = len(e)
            if ne == 3:
                u, v, num = e
            elif ne == 2:
                u, v = e
                num = 1
            else:
                raise NetworkXError("")
            self.decrease_edge(u, v, num)

    def set_num(self, u, v, num):
        if num == 0 and self.has_edge(u, v):
            super().remove_edge(u, v)
        else:
            self[u][v]['num'] = num

    def get_num(self, u, v):
        return self[u][v]['num'] if self.has_edge(u, v) else 0

    def multi_out_degree(self, node):
        return sum([m for _, _, m in self.out_edges(node, data="num")])

    def multi_in_degree(self, node):
        return sum([m for _, _, m in self.in_edges(node, data="num")])
