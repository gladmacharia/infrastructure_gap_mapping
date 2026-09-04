LAYER_CONFIG = {
    "counties": {
        "schema": "boundaries",
        "table": "counties",
        "geometry_type": "polygon",
        "simplify_tolerance": 750,
        "geojson_precision": 4,
    },

    "constituencies": {
        "schema": "boundaries",
        "table": "constituencies",
        "geometry_type": "polygon",
        "simplify_tolerance": 1000,
        "geojson_precision": 4,
    },

    "wards": {
        "schema": "boundaries",
        "table": "wards",
        "geometry_type": "polygon",
        "simplify_tolerance": 1500,
        "geojson_precision": 4,
    },

    "schools": {
        "schema": "education",
        "table": "schools_facilities",
        "geometry_type": "point",
        "simplify_tolerance": 0,
        "geojson_precision": 6,
    },

    "hospitals": {
        "schema": "health",
        "table": "health_facilities",
        "geometry_type": "point",
        "simplify_tolerance": 0,
        "geojson_precision": 6,
    },

    "police": {
        "schema": "interior_security",
        "table": "police_facilities",
        "geometry_type": "point",
        "simplify_tolerance": 0,
        "geojson_precision": 6,
    },

    "roads": {
        "schema": "transport",
        "table": "roads",
        "geometry_type": "line",
        "simplify_tolerance": 250,
        "geojson_precision": 5,
    },

    "fiber": {
        "schema": "utilities",
        "table": "fiber",
        "geometry_type": "line",
        "simplify_tolerance": 0,
        "geojson_precision": 5,
    },

    "electricity": {
        "schema": "utilities",
        "table": "electricity",
        "geometry_type": "line",
        "simplify_tolerance": 500,
        "geojson_precision": 5,
    },
}


def get_layer_config(layer_name: str):
    if layer_name not in LAYER_CONFIG:
        raise ValueError(f"Unknown layer: {layer_name}")

    return LAYER_CONFIG[layer_name]


def get_layer_bbox_query(
    schema: str,
    table: str,
    simplify_tolerance: float = 0,
    geojson_precision: int = 6,
) -> str:

    if simplify_tolerance > 0:

        geometry_expression = f"""
            ST_SimplifyPreserveTopology(
                geometry,
                {simplify_tolerance}
            )
        """

    else:

        geometry_expression = "geometry"

    return f"""
        SELECT
            *,
            ST_AsGeoJSON(
                ST_Transform(
                    {geometry_expression},
                    4326
                ),
                {geojson_precision}
            ) AS geojson_geometry

        FROM {schema}.{table}

        WHERE geometry && ST_Transform(
            ST_MakeEnvelope(
                $1,
                $2,
                $3,
                $4,
                4326
            ),
            32737
        )

        AND ST_Intersects(
            geometry,
            ST_Transform(
                ST_MakeEnvelope(
                    $1,
                    $2,
                    $3,
                    $4,
                    4326
                ),
                32737
            )
        )

        LIMIT $5
    """


def get_dataset_count_query(schema: str, table: str) -> str:
    return f"""
        SELECT COUNT(*)
        FROM {schema}.{table}
    """