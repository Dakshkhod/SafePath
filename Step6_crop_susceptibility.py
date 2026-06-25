import numpy as np
import rasterio
from rasterio.windows import from_bounds
import osmnx as ox

SRC = "global-landslide-susceptibility-map-2-27-23.tif"
OUT = "mandi_susceptibility.tif"
PAD = 0.02

nodes = ox.graph_to_gdfs(ox.load_graphml("mandi.graphml"), edges=False)
lon_min, lat_min, lon_max, lat_max = nodes.total_bounds
print(f"Study-area bounds: lon {lon_min:.4f}..{lon_max:.4f}, lat {lat_min:.4f}..{lat_max:.4f}")

with rasterio.open(SRC) as src:
    print("\n--- Source raster ---")
    print("CRS          :", src.crs)
    print("no-data      :", src.nodata)
    print("dtype        :", src.dtypes[0])
    print("size (W x H) :", src.width, "x", src.height)

    window = from_bounds(
        lon_min - PAD,
        lat_min - PAD,
        lon_max + PAD,
        lat_max + PAD,
        transform=src.transform,
    )

    data = src.read(1, window=window)
    win_transform = src.window_transform(window)

    profile = src.profile.copy()
    profile.update(
        height=data.shape[0],
        width=data.shape[1],
        transform=win_transform,
    )

with rasterio.open(OUT, "w", **profile) as dst:
    dst.write(data, 1)

print(f"\nSaved cropped raster to {OUT} (shape {data.shape[0]} rows x {data.shape[1]} cols)")

vals = np.unique(data)
print("\nUnique values in the Mandi crop:", vals)