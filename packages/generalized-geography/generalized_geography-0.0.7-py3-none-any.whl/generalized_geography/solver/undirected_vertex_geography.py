import networkx as nx


def remove_loops(graph: nx.Graph):
    loop_nodes = [node for node in graph if graph.has_edge(node, node)]
    for node in loop_nodes:
        return graph.remove_edge(node, node)

