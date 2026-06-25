import os
import osmnx as ox
import networkx as nx
import pandas as pd

CANDIDATES = {
    "Shimla":    "Shimla, Himachal Pradesh, India",
    "Mandi":     "Mandi, Himachal Pradesh, India",
    "Joshimath": "Joshimath, Uttarakhand, India",  
}

CATALOG_CSV = "nasa_global_landslide_catalog.csv"

catalog = None
if os.path.exists(CATALOG_CSV):
    catalog = pd.read_csv(CATALOG_CSV)
    print("Catalog columns:", list(catalog.columns), "\n") 
else:
    print(f"[!] '{CATALOG_CSV}' not found -- running network checks only.")
    print("    Download it from landslides.nasa.gov and re-run for catalog counts.\n")


def network_redundancy(G):
    """Three views of 'are there alternative routes here?'"""
    stats = ox.basic_stats(G)
    spn_avg = stats["streets_per_node_avg"]          
    props = stats.get("streets_per_node_proportions") or stats.get("streets_per_node_proportion")
    dead_ends = props.get(1, 0.0)                      

    Gu = ox.convert.to_undirected(G)
    loops = Gu.number_of_edges() - Gu.number_of_nodes() + nx.number_connected_components(Gu)
    loops_per_node = loops / Gu.number_of_nodes()
    return spn_avg, dead_ends, loops_per_node


def catalog_count(G):
    """How many catalog points fall inside this graph's bounding box?"""
    if catalog is None:
        return None, None
    nodes = ox.graph_to_gdfs(G, edges=False)
    lon_min, lat_min, lon_max, lat_max = nodes.total_bounds   
    in_box = catalog[
        catalog["latitude"].between(lat_min, lat_max)
        & catalog["longitude"].between(lon_min, lon_max)
    ]
    if "location_accuracy" in catalog.columns:
        vague = ["50km", "25km", "unknown"]
        precise = in_box[~in_box["location_accuracy"].isin(vague)]
    else:
        precise = in_box
    return len(in_box), len(precise)

print("=== SafePath candidate comparison ===\n")
for name, query in CANDIDATES.items():
    try:
        print(f"Downloading {name} (this hits OpenStreetMap, give it a moment)...")
        G = ox.graph_from_place(query, network_type="drive")
        spn, de, lpn = network_redundancy(G)
        total, precise = catalog_count(G)

        print(f"\n--- {name} ---")
        print(f"  nodes / edges        : {G.number_of_nodes()} / {G.number_of_edges()}")
        print(f"  streets_per_node_avg : {spn:.2f}    (~2 = linear, 3+ = meshy)")
        print(f"  dead-end fraction    : {de:.2f}     (high = dendritic/linear)")
        print(f"  loops per node       : {lpn:.3f}   (<=0.05 reject, 0.1-0.3 good)")
        if total is not None:
            print(f"  catalog pts in box   : {total}  (precise enough to use: {precise})")
        print()
    except Exception as e:
        print(f"  [!] {name} failed: {e}\n")
