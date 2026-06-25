"""
SafePath -- Joshimath control
Joshimath has no OSM area boundary, so graph_from_place fails on it.
We download a fixed-radius disc around its coordinates instead, then run the
SAME redundancy + catalog checks as preflight.py so the numbers are comparable.

Caveat to record for your writeup: Shimla/Mandi were defined by their
administrative boundary; Joshimath here by a 15 km radius. The area-definition
method differs -- but it's more than enough to show whether the network is
near-linear, which is all this control is for.

Run inside the `safepath` env:   python joshimath_control.py
"""

import os
import osmnx as ox
import networkx as nx
import pandas as pd

CATALOG_CSV = "nasa_global_landslide_catalog.csv"
JOSHIMATH = (30.555, 79.565)   # (latitude, longitude)
RADIUS_M = 15000               # 15 km each way -> ~30 km across, within the brief's 10-30 km

# --- load the catalog (same file as before) ---
catalog = pd.read_csv(CATALOG_CSV) if os.path.exists(CATALOG_CSV) else None

# --- download the network as a disc around the point ---
print(f"Downloading Joshimath within {RADIUS_M/1000:.0f} km of {JOSHIMATH}...")
G = ox.graph_from_point(JOSHIMATH, dist=RADIUS_M, network_type="drive")

# --- redundancy (identical logic to preflight.py) ---
stats = ox.basic_stats(G)
spn_avg = stats["streets_per_node_avg"]
props = stats.get("streets_per_node_proportions") or stats.get("streets_per_node_proportion")
dead_ends = props.get(1, 0.0)

Gu = ox.convert.to_undirected(G)   # collapse the directed multigraph first
loops = Gu.number_of_edges() - Gu.number_of_nodes() + nx.number_connected_components(Gu)
loops_per_node = loops / Gu.number_of_nodes()

# --- catalog count inside this graph's bounding box ---
total = precise = None
if catalog is not None:
    nodes = ox.graph_to_gdfs(G, edges=False)
    lon_min, lat_min, lon_max, lat_max = nodes.total_bounds
    in_box = catalog[
        catalog["latitude"].between(lat_min, lat_max)
        & catalog["longitude"].between(lon_min, lon_max)
    ]
    if "location_accuracy" in catalog.columns:
        precise_df = in_box[~in_box["location_accuracy"].isin(["50km", "25km", "unknown"])]
    else:
        precise_df = in_box
    total, precise = len(in_box), len(precise_df)

# --- report, same format as preflight.py ---
print("\n--- Joshimath (15 km radius control) ---")
print(f"  nodes / edges        : {G.number_of_nodes()} / {G.number_of_edges()}")
print(f"  streets_per_node_avg : {spn_avg:.2f}    (~2 = linear, 3+ = meshy)")
print(f"  dead-end fraction    : {dead_ends:.2f}     (high = dendritic/linear)")
print(f"  loops per node       : {loops_per_node:.3f}   (<=0.05 reject, 0.1-0.3 good)")
if total is not None:
    print(f"  catalog pts in box   : {total}  (precise enough to use: {precise})")
