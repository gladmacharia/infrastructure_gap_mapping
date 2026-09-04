import pandas as pd
import geopandas as gpd
from infrastructure_gap.config import rename_columns


# reproject

def reproject_gdf(gdf, target_crs):

    return gdf.to_crs(target_crs)

# centroids for polygons

def polygon_to_centroid(polygons_gdf):

    centroids = polygons_gdf.copy()
    centroids["geometry"] = centroids.geometry.centroid

    return centroids

#Merging points and centroids
def merge_layers(points_gdf,centroids_gdf):

    merged = pd.concat([points_gdf, centroids_gdf], ignore_index=True)

    return gpd.GeoDataFrame(merged, geometry="geometry", crs=points_gdf.crs)

def remove_duplicates(merged_gdf):

    merged_gdf = merged_gdf.drop_duplicates()

    merged_gdf = merged_gdf.drop_duplicates(subset="geometry", keep="first")

    merged_gdf = merged_gdf.reset_index(drop=True)

    return merged_gdf

def build_facilities(points_gdf, polygons_gdf):

    centroids_gdf = polygon_to_centroid(polygons_gdf)

    merged_gdf = merge_layers(points_gdf, centroids_gdf)

    cleaned_gdf = remove_duplicates(merged_gdf)

    return cleaned_gdf

def rename_dataset_columns(name, gdf):

    columns = rename_columns.get(name, {})

    return gdf.rename(columns=columns)