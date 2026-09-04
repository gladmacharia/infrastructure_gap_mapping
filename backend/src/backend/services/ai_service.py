from pathlib import Path
import json
import os

from dotenv import load_dotenv
from groq import AsyncGroq

from backend.core import database
from backend.schemas.responses import AIIntent

from backend.db.analysis_queries import (
    get_wards_zero_hospitals_query,
    get_wards_zero_police_query,
    get_counties_by_school_count_query,
    get_counties_poor_facility_coverage_query,
    get_counties_zero_hospitals_query,
    get_counties_zero_police_query,
    get_counties_zero_schools_query,
    get_wards_zero_schools_query,
    get_wards_no_major_facilities_query,
    get_counties_most_hospitals_query,
    get_counties_most_police_query,
    get_counties_fewest_schools_query,
    get_wards_most_schools_query,
    get_wards_most_hospitals_query,
    get_schools_far_from_hospitals_query,
    get_facilities_no_road_access_query,
    get_facilities_without_fiber_query,
    get_counties_without_electricity_query,
    get_wards_highest_population_query,
    get_wards_lowest_population_query,
    get_counties_highest_population_query,
    get_counties_lowest_population_query,
    get_counties_hospital_population_ratio_query,
    get_counties_school_population_ratio_query,
    get_high_population_wards_without_hospitals_query,
    get_high_population_wards_without_major_facilities_query,
)


base_dir = Path(__file__).resolve().parents[4]

load_dotenv(base_dir/".env")

GROQ_API_KEY=os.getenv("GROQ_API")

GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY is not configured.")

groq_client = AsyncGroq(api_key=GROQ_API_KEY)

AI_SYSTEM_PROMPT = """
You are the AI intent interpreter for a Kenya Infrastructure
Gap Mapping application.

Your ONLY job is to understand the user's natural-language
question and convert it into one supported analysis intent.

DO NOT:
- write SQL
- write Python
- invent database tables
- invent database columns
- perform spatial calculations
- return GeoJSON
- answer the question directly

Return ONLY valid JSON.

The JSON format is:

{
    "intent": "supported_intent",
    "distance_meters": number_or_null,
    "limit": number_or_null
}


SUPPORTED INTENTS
=================

counties_without_hospitals
- Counties that have no hospitals.

counties_without_police
- Counties that have no police facilities.

counties_without_schools
- Counties that have no schools.

wards_without_hospitals
- Wards that have no hospitals.

wards_without_police
- Wards that have no police facilities.

wards_without_schools
- Wards that have no schools.

wards_without_major_facilities
- Wards that have none of:
  schools, hospitals, police.

counties_most_hospitals
- Counties ranked by number of hospitals, highest first.

counties_most_police
- Counties ranked by number of police facilities, highest first.

counties_fewest_schools
- Counties ranked by number of schools, lowest first.

wards_most_schools
- Wards ranked by number of schools, highest first.

wards_most_hospitals
- Wards ranked by number of hospitals, highest first.

schools_far_from_hospitals
- Schools whose nearest hospital is farther than
  the requested distance.

facilities_without_road_access
- Schools, hospitals or police facilities that do not
  have a road within the requested distance.

facilities_without_fiber
- Schools, hospitals or police facilities that do not
  have fiber within the requested distance.

counties_without_electricity
- Counties that do not intersect the electricity network.

wards_highest_population
- Wards ranked by population, highest first.

wards_lowest_population
- Wards ranked by population, lowest first.

counties_highest_population
- Counties ranked by population, highest first.

counties_lowest_population
- Counties ranked by population, lowest first.

hospitals_per_10000
- Hospitals per 10,000 population by county.

schools_per_10000
- Schools per 10,000 population by county.

high_population_wards_without_hospitals
- High-population wards that have no hospitals.

high_population_wards_without_major_facilities
- High-population wards that have none of:
  schools, hospitals or police.

counties_by_school_count
- County with the highest number of schools.

counties_poor_facility_coverage
- Counties with poor facility coverage.

unsupported
- Anything that does not correspond to a supported analysis.


DISTANCE RULES
==============

If the user specifies a distance, convert it to meters.

Examples:

10 km = 10000
5 km = 5000
2 km = 2000
1 km = 1000
500 metres = 500
250 meters = 250


EXAMPLES
========

User:
"Which schools are more than 10 km from a hospital?"

Return:

{
    "intent": "schools_far_from_hospitals",
    "distance_meters": 10000,
    "limit": null
}


User:
"Which schools are more than 5 kilometres away from
the nearest hospital?"

Return:

{
    "intent": "schools_far_from_hospitals",
    "distance_meters": 5000,
    "limit": null
}


User:
"Which facilities have no road within 500 metres?"

Return:

{
    "intent": "facilities_without_road_access",
    "distance_meters": 500,
    "limit": null
}


User:
"Which facilities have no road within 1 km?"

Return:

{
    "intent": "facilities_without_road_access",
    "distance_meters": 1000,
    "limit": null
}


User:
"Which wards have zero hospitals?"

Return:

{
    "intent": "wards_without_hospitals",
    "distance_meters": null,
    "limit": null
}


User:
"Which high population wards have no hospitals?"

Return:

{
    "intent": "high_population_wards_without_hospitals",
    "distance_meters": null,
    "limit": 50
}


User:
"Which counties have the most hospitals?"

Return:

{
    "intent": "counties_most_hospitals",
    "distance_meters": null,
    "limit": null
}


User:
"Which counties have the highest population?"

Return:

{
    "intent": "counties_highest_population",
    "distance_meters": null,
    "limit": null
}


For unsupported questions return:

{
    "intent": "unsupported",
    "distance_meters": null,
    "limit": null
}
"""

async def interpret_question(question: str) -> AIIntent:
    response = await groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "system",
                "content": AI_SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": question,
            },
        ],
        temperature=0,
        response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content

    if not content:
        raise ValueError("AI returned an empty response.")

    try:
        data = json.loads(content)
    except json.JSONDecodeError as error:
        raise ValueError("AI returned invalid JSON.") from error

    return AIIntent.model_validate(data)


async def run_query(query: str, *args):
    async with database.pool.acquire() as connection:
        rows = await connection.fetch(query, *args)

    features = []

    for row in rows:
        properties = dict(row)

        geometry_json = properties.pop("geometry", None)

        if geometry_json is None:
            continue

        geometry = json.loads(geometry_json)

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


def result(message: str, geojson: dict):
    return {
        "message": message,
        "geojson": geojson,
    }


async def wards_zero_hospitals():
    geojson = await run_query(get_wards_zero_hospitals_query())

    count = len(geojson["features"])

    return result(
        f"I found {count} wards with no hospital facilities.",
        geojson,
    )


async def wards_zero_police():
    geojson = await run_query(get_wards_zero_police_query())

    count = len(geojson["features"])

    return result(
        f"I found {count} wards with no police facilities.",
        geojson,
    )


async def counties_by_school_count():
    geojson = await run_query(get_counties_by_school_count_query())

    if not geojson["features"]:
        return result(
            "No county school data was found.",
            geojson,
        )

    top = geojson["features"][0]

    properties = top["properties"]

    county_name = properties.get("county_name", "The leading county")

    school_count = properties.get("school_count", 0)

    return result(
        (
            f"{county_name} has the highest number "
            f"of schools with {school_count} facilities."
        ),
        geojson,
    )


async def counties_poor_facility_coverage():
    geojson = await run_query(get_counties_poor_facility_coverage_query())

    count = len(geojson["features"])

    return result(
        (
            f"I found {count} counties with a "
            "facility coverage score of 1 or less "
            "across schools, hospitals and police."
        ),
        geojson,
    )


async def counties_zero_hospitals():
    geojson = await run_query(get_counties_zero_hospitals_query())

    count = len(geojson["features"])

    return result(
        f"I found {count} counties with no hospitals.",
        geojson,
    )


async def counties_zero_police():
    geojson = await run_query(get_counties_zero_police_query())

    count = len(geojson["features"])

    return result(
        f"I found {count} counties with no police facilities.",
        geojson,
    )


async def counties_zero_schools():
    geojson = await run_query(get_counties_zero_schools_query())

    count = len(geojson["features"])

    return result(
        f"I found {count} counties with no schools.",
        geojson,
    )


async def wards_zero_schools():
    geojson = await run_query(get_wards_zero_schools_query())

    count = len(geojson["features"])

    return result(
        f"I found {count} wards with no schools.",
        geojson,
    )


async def wards_no_major_facilities():
    geojson = await run_query(get_wards_no_major_facilities_query())

    count = len(geojson["features"])

    return result(
        (
            f"I found {count} wards with no schools, "
            "hospitals or police facilities."
        ),
        geojson,
    )


async def counties_most_hospitals():
    geojson = await run_query(get_counties_most_hospitals_query())

    return result(
        "These are the counties with the highest number of hospitals.",
        geojson,
    )


async def counties_most_police():
    geojson = await run_query(get_counties_most_police_query())

    return result(
        "These are the counties with the highest number of police facilities.",
        geojson,
    )


async def counties_fewest_schools():
    geojson = await run_query(get_counties_fewest_schools_query())

    return result(
        "These are the counties with the fewest schools.",
        geojson,
    )


async def wards_most_schools():
    geojson = await run_query(get_wards_most_schools_query())

    return result(
        "These are the wards with the highest number of schools.",
        geojson,
    )


async def wards_most_hospitals():
    geojson = await run_query(get_wards_most_hospitals_query())

    return result(
        "These are the wards with the highest number of hospitals.",
        geojson,
    )


async def schools_far_from_hospitals(distance_meters: float = 10000):
    geojson = await run_query(
        get_schools_far_from_hospitals_query(distance_meters),
        distance_meters,
    )

    count = len(geojson["features"])
    distance_km = distance_meters / 1000

    return result(
        f"I found {count} schools located more than {distance_km:g} km from their nearest hospital.",
        geojson,
    )


async def facilities_no_road_access(distance_meters: float = 500):
    geojson = await run_query(
        get_facilities_no_road_access_query(distance_meters),
        distance_meters,
    )

    count = len(geojson["features"])

    distance_meters_value = distance_meters

    if distance_meters_value >= 1000:
        distance_text = f"{distance_meters_value / 1000:g} km"
    else:
        distance_text = f"{distance_meters_value:g} metres"

    return result(
        f"I found {count} facilities with no road within {distance_text}.",
        geojson,
    )


async def facilities_without_fiber():
    geojson = await run_query(get_facilities_without_fiber_query())

    count = len(geojson["features"])

    return result(
        (
            f"I found {count} schools, hospitals or police "
            "facilities that are not within 500 metres of fiber."
        ),
        geojson,
    )


async def counties_without_electricity():
    geojson = await run_query(get_counties_without_electricity_query())

    count = len(geojson["features"])

    return result(
        f"I found {count} counties that do not intersect the electricity network.",
        geojson,
    )


async def wards_highest_population():
    geojson = await run_query(get_wards_highest_population_query())

    return result(
        "These are the 20 wards with the highest population.",
        geojson,
    )


async def wards_lowest_population():
    geojson = await run_query(get_wards_lowest_population_query())

    return result(
        "These are the 20 wards with the lowest population.",
        geojson,
    )


async def counties_highest_population():
    geojson = await run_query(get_counties_highest_population_query())

    return result(
        "These are the 10 counties with the highest population.",
        geojson,
    )


async def counties_lowest_population():
    geojson = await run_query(get_counties_lowest_population_query())

    return result(
        "These are the 10 counties with the lowest population.",
        geojson,
    )


async def counties_hospital_population_ratio():
    geojson = await run_query(get_counties_hospital_population_ratio_query())

    return result(
        (
            "These counties are ranked by hospitals per "
            "10,000 people, with the lowest ratios first."
        ),
        geojson,
    )


async def counties_school_population_ratio():
    geojson = await run_query(get_counties_school_population_ratio_query())

    return result(
        (
            "These counties are ranked by schools per "
            "10,000 people, with the lowest ratios first."
        ),
        geojson,
    )


async def high_population_wards_without_hospitals():
    geojson = await run_query(get_high_population_wards_without_hospitals_query())

    return result(
        (
            "These are high-population wards with no "
            "hospital facility, ranked by population."
        ),
        geojson,
    )


async def high_population_wards_without_major_facilities():
    geojson = await run_query(get_high_population_wards_without_major_facilities_query())

    return result(
        (
            "These are high-population wards with no "
            "school, hospital or police facility."
        ),
        geojson,
    )