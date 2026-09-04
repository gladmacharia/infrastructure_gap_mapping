import json

from fastapi import APIRouter, Query

from backend.core import database


router = APIRouter(
    prefix="/api/search",
    tags=["Search"],
)


def clean_search_term(value: str) -> str:
    value = value.strip()

    suffixes = [" county", " constituency", " ward"]

    lower_value = value.lower()

    for suffix in suffixes:
        if lower_value.endswith(suffix):
            value = value[:-len(suffix)].strip()
            break

    return value


@router.get("")
async def search_locations(q: str = Query(..., min_length=1)):
    search_term = clean_search_term(q)

    query = """
    WITH exact_matches AS (
        SELECT
            1 AS priority, 'county' AS location_type, county_name AS name, county_name,
            NULL::text AS constituency_name, NULL::text AS ward_name,
            ST_AsGeoJSON(ST_Transform(ST_SimplifyPreserveTopology(geometry, 750), 4326), 5) AS geojson_geometry
        FROM boundaries.counties
        WHERE LOWER(TRIM(county_name)) = LOWER($1)

        UNION ALL

        SELECT
            2 AS priority, 'constituency' AS location_type, constituency_name AS name, county_name,
            constituency_name, NULL::text AS ward_name,
            ST_AsGeoJSON(ST_Transform(ST_SimplifyPreserveTopology(geometry, 1000), 4326), 5) AS geojson_geometry
        FROM boundaries.constituencies
        WHERE LOWER(TRIM(constituency_name)) = LOWER($1)

        UNION ALL

        SELECT
            3 AS priority, 'ward' AS location_type, ward_name AS name, county_name,
            constituency_name, ward_name,
            ST_AsGeoJSON(ST_Transform(ST_SimplifyPreserveTopology(geometry, 1500), 4326), 5) AS geojson_geometry
        FROM boundaries.wards
        WHERE LOWER(TRIM(ward_name)) = LOWER($1)
    ),

    partial_matches AS (
        SELECT
            4 AS priority, 'county' AS location_type, county_name AS name, county_name,
            NULL::text AS constituency_name, NULL::text AS ward_name,
            ST_AsGeoJSON(ST_Transform(ST_SimplifyPreserveTopology(geometry, 750), 4326), 5) AS geojson_geometry
        FROM boundaries.counties
        WHERE LOWER(county_name) LIKE LOWER($2)

        UNION ALL

        SELECT
            5 AS priority, 'constituency' AS location_type, constituency_name AS name, county_name,
            constituency_name, NULL::text AS ward_name,
            ST_AsGeoJSON(ST_Transform(ST_SimplifyPreserveTopology(geometry, 1000), 4326), 5) AS geojson_geometry
        FROM boundaries.constituencies
        WHERE LOWER(constituency_name) LIKE LOWER($2)

        UNION ALL

        SELECT
            6 AS priority, 'ward' AS location_type, ward_name AS name, county_name,
            constituency_name, ward_name,
            ST_AsGeoJSON(ST_Transform(ST_SimplifyPreserveTopology(geometry, 1500), 4326), 5) AS geojson_geometry
        FROM boundaries.wards
        WHERE LOWER(ward_name) LIKE LOWER($2)
    )

    SELECT * FROM exact_matches

    UNION ALL

    SELECT * FROM partial_matches
    WHERE NOT EXISTS (
        SELECT 1 FROM exact_matches
    )

    ORDER BY priority
    LIMIT 20
"""
    partial_term = f"%{search_term}%"

    async with database.pool.acquire() as connection:
        rows = await connection.fetch(query, search_term, partial_term)

    features = []

    for row in rows:
        geometry = json.loads(row["geojson_geometry"])

        properties = {
            "location_type": row["location_type"],
            "name": row["name"],
            "county_name": row["county_name"],
            "constituency_name": row["constituency_name"],
            "ward_name": row["ward_name"],
        }

        features.append({
            "type": "Feature",
            "geometry": geometry,
            "properties": properties,
        })

    return {
        "type": "FeatureCollection",
        "features": features,
    }