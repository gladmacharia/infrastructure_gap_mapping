from infrastructure_gap.config import geopackage_path

import geopandas as gpd

gpkg_path = geopackage_path

raw_data = {
    "counties": "county",
    "constituencies": "constituency",
    "wards": "wards",
    "health_points": "health_facilities_points",
    "health_polygons": "health_facilities_polygons",
    "police_points" : "police_points",
    "police_polygons" : "police_polygons",
    "schools_points": "schools_points",
    "schools_polygons": "schools_polygons",
    "fiber": "fiber_2021",
    "roads" : "roads",
    "electricity": "electricity_25"
    }

def load_raw_data():

    datasets = {}

    for key, layer in raw_data.items():
        datasets[key] = gpd.read_file(gpkg_path, layer=layer)

    return datasets
