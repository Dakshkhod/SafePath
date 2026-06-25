import osmnx as ox
import networkx as nx

CENTER = (31.708679, 76.932029)
RADIUS_M = 12000

print("Downloading the Mandi road network from OpenStreetMap...")

G = ox.graph_from_point(
    CENTER,
    dist=RADIUS_M,
    dist_type="bbox",
    network_type="drive",
)

print(f"Done: {G.number_of_nodes()} intersections, {G.number_of_edges()} road segments.")

n_components = nx.number_weakly_connected_components(G)
print(f"Weakly connected components: {n_components}   (want 1 = fully connected)")

ox.save_graphml(G, filepath="mandi.graphml")
print("Saved graph to mandi.graphml")

nodes = ox.graph_to_gdfs(G, edges=False)
lon_min, lat_min, lon_max, lat_max = nodes.total_bounds

print("\nBounding box:")
print(f"  lat: {lat_min:.6f} to {lat_max:.6f}")
print(f"  lon: {lon_min:.6f} to {lon_max:.6f}")

ox.plot_graph(
    G,
    node_size=4,
    edge_linewidth=0.5,
    save=True,
    filepath="mandi_network.png",
    dpi=200,
)