import geopandas as gpd

def check_crs(gdf):
    return gdf.crs


def check_geometry_type(gdf):
    return gdf.geom_type.value_counts()


def check_invalid_geometries(gdf):
    return (~gdf.is_valid).sum()


def check_empty_geometries(gdf):
    return gdf.geometry.is_empty.sum()


def check_duplicate_rows(gdf):
    return gdf.duplicated().sum()


def check_duplicate_geometries(gdf):
    return gdf.geometry.duplicated().sum()


def check_null_values(gdf):
    return gdf.isnull().sum()


def dataset_summary(gdf):

    summary = {
        "Features": len(gdf),
        "CRS": gdf.crs,
        "Geometry": check_geometry_type(gdf).to_dict(),
        "Invalid Geometries": check_invalid_geometries(gdf),
        "Empty Geometries": check_empty_geometries(gdf),
        "Duplicate Rows": check_duplicate_rows(gdf),
        "Duplicate Geometries": check_duplicate_geometries(gdf)
    }

    return summary

def validate_dataset(name, gdf):
    """
    Prints a validation report for a dataset.
    """

    print("=" * 60)
    print(f"Dataset: {name}")
    print("=" * 60)

    summary = dataset_summary(gdf)

    for key, value in summary.items():
        print(f"{key}: {value}")

    print("\nMissing Values")
    print(check_null_values(gdf))