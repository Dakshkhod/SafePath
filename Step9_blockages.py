import json
import numpy as np
import pandas as pd
import geopandas as gpd
import osmnx as ox

catalogFile = "nasa_global_landslide_catalog.csv"
maxSnapMeters = 200
vagueAccuracies = ["25km", "50km", "unknown"]
bboxPad = 0.02

roadGraph = ox.load_graphml("mandi.graphml")
lonMin, latMin, lonMax, latMax = ox.graph_to_gdfs(roadGraph, edges=False).total_bounds

catalog = pd.read_csv(catalogFile)
nearbyLandslides = catalog[
    catalog["latitude"].between(latMin - bboxPad, latMax + bboxPad)
    & catalog["longitude"].between(lonMin - bboxPad, lonMax + bboxPad)
]

if "location_accuracy" in catalog.columns:
    nearbyLandslides = nearbyLandslides[
        ~nearbyLandslides["location_accuracy"].isin(vagueAccuracies)
    ]

print("Usable landslides in the Mandi area:", len(nearbyLandslides))

if len(nearbyLandslides) == 0:
    raise SystemExit("No usable landslides found in the study area.")

projectedGraph = ox.project_graph(roadGraph)

landslidePoints = gpd.GeoDataFrame(
    nearbyLandslides,
    geometry=gpd.points_from_xy(
        nearbyLandslides["longitude"],
        nearbyLandslides["latitude"],
    ),
    crs="EPSG:4326",
).to_crs(projectedGraph.graph["crs"])

nearestRoads, snapDistances = ox.distance.nearest_edges(
    projectedGraph,
    landslidePoints.geometry.x.values,
    landslidePoints.geometry.y.values,
    return_dist=True,
)

blockedRoads = set()
tooFarCount = 0

for road, distance in zip(nearestRoads, snapDistances):
    fromNode, toNode, edgeKey = road

    if distance <= maxSnapMeters:
        blockedRoads.add((int(fromNode), int(toNode), int(edgeKey)))
    else:
        tooFarCount += 1

print(
    f"Snap distance (m): min {np.min(snapDistances):.0f}, "
    f"median {np.median(snapDistances):.0f}, "
    f"max {np.max(snapDistances):.0f}"
)
print("Landslides ignored (nearest road too far):", tooFarCount)
print("Unique blocked roads:", len(blockedRoads))

with open("blocked_edges.json", "w") as outputFile:
    json.dump([list(road) for road in blockedRoads], outputFile)

print("Saved the blocked set to blocked_edges.json")