import osmnx as ox, networkx as nx

G = ox.load_graphml("mandi.graphml")          # load the study-area graph you saved
stats = ox.basic_stats(G)
Gu = ox.convert.to_undirected(G)              # collapse the directed multigraph first
loops = Gu.number_of_edges() - Gu.number_of_nodes() + nx.number_connected_components(Gu)

props = stats.get("streets_per_node_proportions") or stats.get("streets_per_node_proportion")
print(f"nodes                : {G.number_of_nodes()}")
print(f"streets_per_node_avg : {stats['streets_per_node_avg']:.2f}")
print(f"dead-end fraction    : {props.get(1, 0):.2f}")
print(f"loops per node       : {loops / Gu.number_of_nodes():.3f}")