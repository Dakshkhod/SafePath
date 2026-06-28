import heapq
import math
import osmnx as ox

from Step11_dijkstra import cheapest_edge_cost


def haversine_meters(lat1, lon1, lat2, lon2):
    earth_radius = 6371000.0

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(d_phi / 2) ** 2
        + math.cos(phi1)
        * math.cos(phi2)
        * math.sin(d_lambda / 2) ** 2
    )

    return 2 * earth_radius * math.asin(math.sqrt(a))


def a_star(graph, source, target):
    target_lat = graph.nodes[target]["y"]
    target_lon = graph.nodes[target]["x"]

    max_speed_mps = (
        max(d["speed_kph"] for *_, d in graph.edges(keys=True, data=True))
        * 1000
        / 3600
    )

    def heuristic(node):
        node_lat = graph.nodes[node]["y"]
        node_lon = graph.nodes[node]["x"]

        straight_line = haversine_meters(
            node_lat,
            node_lon,
            target_lat,
            target_lon,
        )

        return straight_line / max_speed_mps

    best_cost = {source: 0.0}
    came_from = {}
    settled = set()
    frontier = [(heuristic(source), source)]
    nodes_settled = 0

    while frontier:
        _, current = heapq.heappop(frontier)

        if current in settled:
            continue

        settled.add(current)
        nodes_settled += 1

        if current == target:
            break

        cost_so_far = best_cost[current]

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

                priority = new_cost + heuristic(neighbour)
                heapq.heappush(frontier, (priority, neighbour))

    if target not in came_from and target != source:
        return None, float("inf"), nodes_settled

    path = [target]

    while path[-1] != source:
        path.append(came_from[path[-1]])

    path.reverse()
    return path, best_cost[target], nodes_settled


if __name__ == "__main__":
    from Step11_dijkstra import dijkstra

    road_graph = ox.load_graphml(
        "mandi.graphml",
        edge_dtypes={"cost": float},
    )

    lon_min, lat_min, lon_max, lat_max = (
        ox.graph_to_gdfs(road_graph, edges=False).total_bounds
    )

    source = ox.nearest_nodes(road_graph, lon_min, lat_min)
    target = ox.nearest_nodes(road_graph, lon_max, lat_max)

    d_path, d_cost, d_settled = dijkstra(
        road_graph,
        source,
        target,
    )

    a_path, a_cost, a_settled = a_star(
        road_graph,
        source,
        target,
    )

    print(f"Dijkstra: {len(d_path):>3} nodes, cost {d_cost:.0f} s, settled {d_settled}")
    print(f"A*      : {len(a_path):>3} nodes, cost {a_cost:.0f} s, settled {a_settled}")
    print("Same total cost? ", abs(d_cost - a_cost) < 1e-6)
    print("Identical route? ", d_path == a_path)