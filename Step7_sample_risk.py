import numpy as np
import rasterio
import osmnx as ox

SPACING_M = 40
NODATA = 127
SUSC_RASTER = "mandi_susceptibility.tif"

G = ox.load_graphml("mandi.graphml")
edges = ox.graph_to_gdfs(G, nodes=False)


def sample_points(line, length_m, spacing=SPACING_M):
    n = max(2, int(length_m // spacing) + 1)
    return [
        (p.x, p.y)
        for p in (
            line.interpolate(i / (n - 1), normalized=True)
            for i in range(n)
        )
    ]


worst_class = {}
n_no_valid = 0

with rasterio.open(SUSC_RASTER) as src:
    for (u, v, k), row in edges.iterrows():
        coords = sample_points(row.geometry, row["length"])
        vals = [val[0] for val in src.sample(coords)]
        valid = [c for c in vals if c != NODATA]

        if valid:
            worst_class[(u, v, k)] = int(max(valid))
        else:
            worst_class[(u, v, k)] = 1
            n_no_valid += 1

for (u, v, k), cls in worst_class.items():
    G[u][v][k]["susceptibility"] = cls
    G[u][v][k]["risk"] = (cls - 1) / 4.0

classes = np.array(list(worst_class.values()))

print(f"Edges processed         : {len(classes)}")
print(f"Edges with no valid data: {n_no_valid}")
print("Worst-class distribution:")

for c in range(1, 6):
    print(f"  class {c} (risk {(c - 1) / 4:.2f}): {(classes == c).sum():4d} edges")

ox.save_graphml(G, filepath="mandi.graphml")
print("\nSaved graph with susceptibility and risk on every edge.")