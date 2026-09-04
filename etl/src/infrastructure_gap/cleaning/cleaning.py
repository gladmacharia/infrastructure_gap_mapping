from infrastructure_gap.config import columns_to_keep


def select_columns(name, gdf):

    required_columns = columns_to_keep.get(name)

    if required_columns is None:
        raise ValueError(f"No columns defined for dataset '{name}' in columns_to_keep.")

    missing_columns = [col for col in required_columns if col not in gdf.columns]
    if missing_columns:
        raise ValueError(f"{name} is missing required columns: {missing_columns}")

    return gdf[required_columns].copy()



def remove_duplicate_rows(gdf):
    return gdf.drop_duplicates()



def remove_empty_geometries(gdf):
    return gdf.loc[~gdf.geometry.is_empty].copy()



def repair_geometries(gdf):
    gdf = gdf.copy()

    invalid = ~gdf.geometry.is_valid

    gdf.loc[invalid, "geometry"] = gdf.loc[invalid, "geometry"].make_valid()

    return gdf



def remove_null_geometries(gdf):
    return gdf[gdf.geometry.notnull()].copy()



def reset_index(gdf):
    return gdf.reset_index(drop=True)



def clean_dataset(name,gdf):

    gdf = select_columns(name, gdf)

    gdf = remove_duplicate_rows(gdf)

    gdf = remove_null_geometries(gdf)

    gdf = remove_empty_geometries(gdf)

    gdf = repair_geometries(gdf)

    gdf = reset_index(gdf)


    return gdf

