import networkx as nx
from collections import deque
import generalized_geography as gg

# 그래프에서 중립 노드를 제외하고 모두 삭제하고, 삭제된 노드의 승패 여부를 알려주는 dict 반환


def fastly_classify(graph: gg.UnlabeledMultiDiGraph, verbose=1):
    node_type1, _ = classify_reusable_winlose(graph, verbose)
    remove_2_cycles(graph, verbose)
    node_type2, _ = classify_loop_winlose(graph, verbose)
    return {**node_type1, **node_type2}

# 그래프에서 중립 노드를 제외하고 모두 삭제하고, 모든 노드의 승패 여부를 알려주는 dict 반환


def completely_classify(graph: gg.UnlabeledMultiDiGraph, verbose=1):
    node_type1 = fastly_classify(graph, verbose)
    node_type2 = classify_dfs_winlose(graph)
    return {**node_type1, **node_type2}

# 2 사이클을 이루는 엣지들 삭제 (a,b), (b,a)
# O(E+V)


def remove_2_cycles(graph: gg.UnlabeledMultiDiGraph, verbose=1):

    if verbose == 1:
        print("Remove 2 cycles : ", end="")

    to_remove = []

    # self loop 짝수 개 검출
    for node in graph.nodes:
        m = graph.get_multiplicity(node, node)
        if m >= 2:
            to_remove.append((node, node, m - m % 2))

    # (a,b), (b,a) 꼴 엣지 검출
    for u, v in [(u, v) for u, v in graph.edges if u > v]:
        if graph.has_edge(v, u):
            delete_num = min(graph.get_multiplicity(u, v),
                             graph.get_multiplicity(v, u))
            to_remove.append((u, v, delete_num))
            to_remove.append((v, u, delete_num))

    # 검출한 엣지들 삭제
    graph.remove_edges_from(to_remove)

    if verbose == 1:
        print(sum([m for _, _, m in to_remove]), "edges removed")

    # 삭제된 엣지들 반환
    return to_remove

# 재사용룰에서 필승 또는 필패인 노드들을 삭제하고, 그 노드들의 승패 여부를 알려주는 dict와 최적 경로를 알려주는 digraph 반환
# O(E+V)


def classify_reusable_winlose(graph: gg.UnlabeledMultiDiGraph, verbose=1, sinks=None):
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

# 필승 전략에 루프를 수반하는 노드들을 삭제하고, 그 노드들의 승패 여부를 알려주는 dict와 최적 경로를 알려주는 digraph 반환
# O(E+V)


def classify_loop_winlose(graph: gg.UnlabeledMultiDiGraph, verbose=1, lose_sinks=None, win_sinks=None):

    if verbose == 1:
        print("Classify loop winlose : ", end="")

    node_type = {}
    path_graph = nx.DiGraph()

    # outedge가 없는 노드들
    if not lose_sinks:
        lose_sinks = [node for node, deg in graph.out_degree() if deg == 0]
    # outedge가 loop edge 하나뿐인 노드들
    if not win_sinks:
        win_sinks = win_sinks if win_sinks else [
            node for node, deg in graph.out_degree() if deg == 1 and graph.has_edge(node, node)]

    for n in lose_sinks:
        node_type[n] = "L"
    for n in win_sinks:
        node_type[n] = "W"

    q = deque(lose_sinks + win_sinks)

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
                elif graph.out_degree(pred) == 1 and graph.get_multiplicity(pred, pred) == 1:
                    node_type[pred] = "W"
                    path_graph.add_edge(pred, pred)
                    path_graph.add_edge(pred, node)
                    q.append(pred)

    if verbose == 1:
        win_nodes = [node for node in node_type if node_type[node] == "W"]
        lose_nodes = [node for node in node_type if node_type[node] == "L"]
        print(len(win_nodes), "win,", len(lose_nodes),
              "lose,", len(graph), "remain")

    return node_type, path_graph

# 임계 엣지 반환
# 임계 엣지 : 그래프에서 제거 될 시 fastly_classify 함수에서 분류되는 노드가 적어도 한 개 존재하게 되는 엣지


def get_critical_edges(graph: gg.UnlabeledMultiDiGraph):
    result = []
    for node in graph.nodes:
        outdeg = graph.multi_out_degree(node)

        if outdeg == 1:
            result.append(list(graph.out_edges(node))[0])

        elif outdeg == 2:
            edges = list(graph.out_edges(node, data="multiplicity"))

            if len(edges) == 1:
                continue

            if edges[1] == node:
                result.append((edges[0][0], edges[0][1]))

            elif edges[0] == node:
                result.append((edges[1][0], edges[1][1]))

    return result

# graph에서 node가 주어진 포지션에서 승패 여부를 dfs로 통해 계산하여 반환


def is_win_dfs(graph: gg.UnlabeledMultiDiGraph, node):
    graph_copy = graph.copy()
    node_type = fastly_classify(graph, verbose=0)

    if node in node_type:
        if node_type[node] == "W":
            return True
        else:
            return False

    for succ in graph.successors(node):
        graph_copy = graph.copy()
        graph_copy.remove_edge(node, succ)
        if not is_win_dfs(graph_copy, succ):
            return True
    return False

# graph에서 모든 노드들에 대해서 승패 여부를 dfs로 계산하여 반환


def classify_dfs_winlose(graph: gg.UnlabeledMultiDiGraph):
    return {node: "W" if is_win_dfs(graph, node) else "L" for node in graph}
