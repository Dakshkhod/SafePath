import osmnx as ox

G = ox.load_graphml("mandi.graphml")
print(f"Loaded graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges.")

G = ox.add_edge_speeds(G)
G = ox.add_edge_travel_times(G)

edges = ox.graph_to_gdfs(G, nodes=False)

n_missing = edges["travel_time"].isna().sum()
print(f"\nEdges with missing travel_time: {n_missing}   (want 0)")
print(f"speed_kph   range: {edges['speed_kph'].min():.0f} to {edges['speed_kph'].max():.0f} km/h")
print(f"travel_time range: {edges['travel_time'].min():.0f} to {edges['travel_time'].max():.0f} s")

edges["highway"] = edges["highway"].astype(str)
print("\nMean values by road type:")
print(edges.groupby("highway")[["length", "speed_kph", "travel_time"]].mean().round(1))

ox.save_graphml(G, filepath="mandi.graphml")
print("\nSaved graph with speed_kph and travel_time to mandi.graphml")