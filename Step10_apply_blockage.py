import json
import networkx as nx
import osmnx as ox

road_graph = ox.load_graphml(
    "mandi.graphml",
    edge_dtypes={"cost": float},
)

with open("blocked_edges.json") as block_file:
    blocked_roads = [tuple(road) for road in json.load(block_file)]

print("Blocked roads to apply:", len(blocked_roads))


def make_blocked_graph(base_graph, roads_to_block):
    blocked_graph = base_graph.copy()
    removed_count = 0

    for from_node, to_node, edge_key in roads_to_block:
        if blocked_graph.has_edge(from_node, to_node, edge_key):
            blocked_graph.remove_edge(from_node, to_node, edge_key)
            removed_count += 1

    print(f"Removed {removed_count} of {len(roads_to_block)} roads from the copy")
    return blocked_graph


blocked_graph = make_blocked_graph(road_graph, blocked_roads)

start_node, end_node, _ = blocked_roads[0]

cost_before = nx.shortest_path_length(
    road_graph,
    start_node,
    end_node,
    weight="cost",
)
path_before = nx.shortest_path(
    road_graph,
    start_node,
    end_node,
    weight="cost",
)

print(f"\nBefore blocking: route has {len(path_before)} nodes, cost {cost_before:.0f} s")

try:
    cost_after = nx.shortest_path_length(
        blocked_graph,
        start_node,
        end_node,
        weight="cost",
    )
    path_after = nx.shortest_path(
        blocked_graph,
        start_node,
        end_node,
        weight="cost",
    )

    print(
        f"After blocking : route has {len(path_after)} nodes, "
        f"cost {cost_after:.0f} s (rerouted around the block)"
    )
except nx.NetworkXNoPath:
    print("After blocking : no route exists (that road was the only way through)")