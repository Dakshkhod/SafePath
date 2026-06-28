import heapq
import osmnx as ox


def cheapest_edge_cost(graph, u, v):
    parallel_edges = graph.get_edge_data(u, v)

    if not parallel_edges:
        return None

    usable = [
        data["cost"]
        for data in parallel_edges.values()
        if "cost" in data and data["cost"] < float("inf")
    ]

    return min(usable) if usable else None


def dijkstra(graph, source, target):
    best_cost = {source: 0.0}
    came_from = {}
    settled = set()
    frontier = [(0.0, source)]
    nodes_settled = 0

    while frontier:
        cost_so_far, current = heapq.heappop(frontier)

        if current in settled:
            continue

        settled.add(current)
        nodes_settled += 1

        if current == target:
            break

        for neighbour in graph.successors(current):
            if neighbour in settled:
                continue

            step = cheapest_edge_cost(graph, current, neighbour)

            if step is None:
                continue

            new_cost = cost_so_far + step

            if new_cost < best_cost.get(neighbour, float("inf")):
                best_cost[neighbour] = new_cost
                came_from[neighbour] = current
                heapq.heappush(frontier, (new_cost, neighbour))

    if target not in came_from and target != source:
        return None, float("inf"), nodes_settled

    path = [target]

    while path[-1] != source:
        path.append(came_from[path[-1]])

    path.reverse()
    return path, best_cost[target], nodes_settled


if __name__ == "__main__":
    road_graph = ox.load_graphml(
        "mandi.graphml",
        edge_dtypes={"cost": float},
    )

    lon_min, lat_min, lon_max, lat_max = (
        ox.graph_to_gdfs(road_graph, edges=False).total_bounds
    )

    source = ox.nearest_nodes(road_graph, lon_min, lat_min)
    target = ox.nearest_nodes(road_graph, lon_max, lat_max)

    path, total_cost, nodes_settled = dijkstra(
        road_graph,
        source,
        target,
    )

    if path is None:
        print("No route exists between those two points.")
    else:
        print(f"Route found : {len(path)} nodes")
        print(f"Total cost  : {total_cost:.0f} s")
        print(f"Nodes settled (explored): {nodes_settled}")