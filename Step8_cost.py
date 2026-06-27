import osmnx as ox

ALPHA = 1.0


def add_risk_adjusted_cost(G, alpha):
    for u, v, k, data in G.edges(keys=True, data=True):
        travel_time = float(data["travel_time"])
        risk = float(data["risk"])
        data["cost"] = travel_time * (1.0 + alpha * risk)
    return G


if __name__ == "__main__":
    G = ox.load_graphml("mandi.graphml")
    add_risk_adjusted_cost(G, ALPHA)

    edges = ox.graph_to_gdfs(G, nodes=False)
    mult = edges["cost"].astype(float) / edges["travel_time"].astype(float)

    print(f"alpha = {ALPHA}")
    print(f"edges costed             : {len(edges)}")
    print(
        f"cost / travel_time ratio : {mult.min():.3f} to {mult.max():.3f}"
        f"   (must lie within 1.000 to {1 + ALPHA:.3f})"
    )
    print(f"cost (seconds) range     : {edges['cost'].min():.0f} to {edges['cost'].max():.0f}")

    ox.save_graphml(G, filepath="mandi.graphml")
    print("\nSaved graph with cost on every edge.")