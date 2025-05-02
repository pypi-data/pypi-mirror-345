import networkx as nx
from collections import deque


def fastly_classify(graph: nx.DiGraph, verbose=1):
    remove_loops(graph, verbose)
    node_type, _ = classify_reusable_winlose(graph, verbose)
    return node_type


def completely_classify(graph: nx.DiGraph, verbose=1):
    node_type1 = fastly_classify(graph, verbose)
    node_type2 = classify_dfs_winlose(graph)
    return {**node_type1, **node_type2}


def remove_loops(graph: nx.DiGraph, verbose=1):
    if verbose == 1:
        print("Remove loops : ", end="")

    loop_nodes = [node for node in graph if graph.has_edge(node, node)]
    for node in loop_nodes:
        graph.remove_edge(node, node)

    if verbose == 1:
        print(f"{len(loop_nodes)} edge removed")

    return loop_nodes


def classify_reusable_winlose(graph: nx.DiGraph, verbose=1, sinks=None):
    if verbose == 1:
        print("Classify reusable winlose : ", end="")

    node_type = {}
    path_graph = nx.DiGraph()

    if not sinks:
        sinks = [node for node, deg in graph.out_degree() if deg == 0]

    q = deque()
    for sink in sinks:
        node_type[sink] = "L"
        q.append(sink)

    while q:
        node = q.popleft()
        if node_type[node] == "L":
            preds = [pred for pred in graph.predecessors(
                node) if pred not in node_type]
            graph.remove_node(node)
            for pred in preds:
                node_type[pred] = "W"
                path_graph.add_edge(pred, node)
                q.append(pred)
        else:
            preds = [pred for pred in graph.predecessors(
                node) if pred not in node_type]
            graph.remove_node(node)
            for pred in preds:
                if graph.out_degree(pred) == 0:
                    node_type[pred] = "L"
                    path_graph.add_edge(pred, node)
                    q.append(pred)

    if verbose == 1:
        win_nodes = [node for node in node_type if node_type[node] == "W"]
        lose_nodes = [node for node in node_type if node_type[node] == "L"]
        print(len(win_nodes), "win,", len(lose_nodes),
              "lose,", len(graph), "remain")

    return node_type, path_graph


def is_win_dfs(graph: nx.DiGraph, node):
    graph_copy = graph.copy()
    node_type = fastly_classify(graph, verbose=0)

    if node in node_type:
        if node_type[node] == "W":
            return True
        else:
            return False

    for succ in graph.successors(node):
        graph_copy = graph.copy()
        graph_copy.remove_node(node)
        if not is_win_dfs(graph_copy, succ):
            return True

    return False


def classify_dfs_winlose(graph: nx.DiGraph):
    return {node: "W" if is_win_dfs(graph, node) else "L" for node in graph}
