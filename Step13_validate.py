import json
import math
import networkx as nx
import osmnx as ox

from Step11_dijkstra import dijkstra
from Step12_astar import a_star, haversine_meters

road_graph = ox.load_graphml(
    "mandi.graphml",
    edge_dtypes={"cost": float},
)

lon_min, lat_min, lon_max, lat_max = (
    ox.graph_to_gdfs(road_graph, edges=False).total_bounds
)

source = ox.nearest_nodes(road_graph, lon_min, lat_min)
target = ox.nearest_nodes(road_graph, lon_max, lat_max)

max_speed_mps = (
    max(d["speed_kph"] for *_, d in road_graph.edges(keys=True, data=True))
    * 1000
    / 3600
)


def nx_heuristic(node, goal):
    return (
        haversine_meters(
            road_graph.nodes[node]["y"],
            road_graph.nodes[node]["x"],
            road_graph.nodes[goal]["y"],
            road_graph.nodes[goal]["x"],
        )
        / max_speed_mps
    )


def build_blocked_graph():
    with open("blocked_edges.json") as f:
        blocked_roads = [tuple(road) for road in json.load(f)]

    blocked = road_graph.copy()

    for from_node, to_node, edge_key in blocked_roads:
        if blocked.has_edge(from_node, to_node, edge_key):
            blocked.remove_edge(from_node, to_node, edge_key)

    return blocked


def compare(graph, label):
    print(f"\n--- {label} ---")

    if not nx.has_path(graph, source, target):
        my_path, _, _ = dijkstra(graph, source, target)

        if my_path is None:
            print("No route source -> target. agree (both: no path)")
        else:
            print("No route source -> target. MISMATCH (mine found one!)")

        return

    _, my_dijkstra_cost, _ = dijkstra(graph, source, target)
    _, my_astar_cost, _ = a_star(graph, source, target)

    nx_dijkstra_cost = nx.shortest_path_length(
        graph,
        source,
        target,
        weight="cost",
    )

    nx_astar_cost = nx.astar_path_length(
        graph,
        source,
        target,
        heuristic=nx_heuristic,
        weight="cost",
    )

    print(
        f"Dijkstra -- mine: {my_dijkstra_cost:.3f}   "
        f"networkx: {nx_dijkstra_cost:.3f}   "
        f"match: {math.isclose(my_dijkstra_cost, nx_dijkstra_cost, rel_tol=1e-6)}"
    )

    print(
        f"A*       -- mine: {my_astar_cost:.3f}   "
        f"networkx: {nx_astar_cost:.3f}   "
        f"match: {math.isclose(my_astar_cost, nx_astar_cost, rel_tol=1e-6)}"
    )


compare(road_graph, "Unblocked graph")
compare(build_blocked_graph(), "Blocked graph")