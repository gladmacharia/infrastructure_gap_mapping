import json

from backend.core import database

from backend.db.spatial_queries import (
    get_layer_config,
    get_layer_bbox_query,
    get_dataset_count_query,
)

from backend.schemas.requests import BoundingBox


async def get_dataset_count(dataset_name: str) -> int:

    layer_config = get_layer_config(dataset_name)

    query = get_dataset_count_query(
        layer_config["schema"],
        layer_config["table"],
    )

    async with database.pool.acquire() as connection:

        count = await connection.fetchval(query)

    return count


async def get_layer_by_bbox(
    layer_name: str,
    bbox: BoundingBox,
):

    layer_config = get_layer_config(layer_name)

    query = get_layer_bbox_query(
        layer_config["schema"],
        layer_config["table"],
        layer_config.get("simplify_tolerance", 0),
        layer_config.get("geojson_precision", 6),
    )

    async with database.pool.acquire() as connection:

        rows = await connection.fetch(
            query,
            bbox.min_lon,
            bbox.min_lat,
            bbox.max_lon,
            bbox.max_lat,
            bbox.limit,
        )

    features = []

    for row in rows:

        properties = dict(row)

        geometry = json.loads(
            properties.pop("geojson_geometry")
        )

        properties.pop("geometry", None)

        features.append(
            {
                "type": "Feature",
                "geometry": geometry,
                "properties": properties,
            }
        )

    return {
        "type": "FeatureCollection",
        "features": features,
    }