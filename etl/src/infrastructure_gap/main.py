from infrastructure_gap.extraction import load_raw_data
from infrastructure_gap.validation import validate_dataset
from infrastructure_gap.cleaning import clean_dataset
from infrastructure_gap.config import target_crs, columns_to_keep
from infrastructure_gap.transformation import (reproject_gdf, build_facilities, rename_dataset_columns)
from infrastructure_gap.loading import load_all_layers




datasets = load_raw_data()

projected_datasets = {}
failed_datasets = {}

for name, gdf in datasets.items():
    try:
        

        validate_dataset(name, gdf)

        cleaned_dataset = clean_dataset(name, gdf)

        reprojected_dataset = reproject_gdf(cleaned_dataset, target_crs)

        projected_datasets[name] = reprojected_dataset

    except Exception as e:
        failed_datasets[name] = str(e)
        print(f"Failed to process {name}: {e}")

facility_types = [
    "health",
    "police",
    "schools"
]

for facility in facility_types:

    points = projected_datasets[f"{facility}_points"]

    polygons = projected_datasets[f"{facility}_polygons"]

    projected_datasets[f"{facility}_facilities"] = build_facilities(
        points,
        polygons
    )

    del projected_datasets[f"{facility}_points"]
    del projected_datasets[f"{facility}_polygons"]


for name, gdf in projected_datasets.items():

    projected_datasets[name] = rename_dataset_columns(
        name,
        gdf
    )



if projected_datasets:
    load_all_layers(projected_datasets)
else:
    print("No datasets available for loading.")




for dataset, error in failed_datasets.items():
    print(f"{dataset}: {error}")