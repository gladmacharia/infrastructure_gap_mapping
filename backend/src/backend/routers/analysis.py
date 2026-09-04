from fastapi import APIRouter, HTTPException

from backend.schemas.requests import QuestionRequest
from backend.schemas.responses import AnalysisResponse

from backend.services.map_service import get_dataset_count

from backend.services.ai_service import (
    interpret_question,
    wards_zero_hospitals,
    wards_zero_police,
    counties_by_school_count,
    counties_poor_facility_coverage,
    counties_zero_hospitals,
    counties_zero_police,
    counties_zero_schools,
    wards_zero_schools,
    wards_no_major_facilities,
    counties_most_hospitals,
    counties_most_police,
    counties_fewest_schools,
    wards_most_schools,
    wards_most_hospitals,
    schools_far_from_hospitals,
    facilities_no_road_access,
    facilities_without_fiber,
    counties_without_electricity,
    wards_highest_population,
    wards_lowest_population,
    counties_highest_population,
    counties_lowest_population,
    counties_hospital_population_ratio,
    counties_school_population_ratio,
    high_population_wards_without_hospitals,
    high_population_wards_without_major_facilities,
)


router = APIRouter(
    prefix="/api/analysis",
    tags=["Analysis"],
)


async def execute_analysis(
    intent: str,
    distance_meters: float | None = None,
    limit: int | None = None,
):
    if intent == "wards_without_hospitals":
        return await wards_zero_hospitals()

    if intent == "wards_without_police":
        return await wards_zero_police()

    if intent == "counties_by_school_count":
        return await counties_by_school_count()

    if intent == "counties_poor_facility_coverage":
        return await counties_poor_facility_coverage()

    if intent == "counties_without_hospitals":
        return await counties_zero_hospitals()

    if intent == "counties_without_police":
        return await counties_zero_police()

    if intent == "counties_without_schools":
        return await counties_zero_schools()

    if intent == "wards_without_schools":
        return await wards_zero_schools()

    if intent == "wards_without_major_facilities":
        return await wards_no_major_facilities()

    if intent == "counties_most_hospitals":
        return await counties_most_hospitals()

    if intent == "counties_most_police":
        return await counties_most_police()

    if intent == "counties_fewest_schools":
        return await counties_fewest_schools()

    if intent == "wards_most_schools":
        return await wards_most_schools()

    if intent == "wards_most_hospitals":
        return await wards_most_hospitals()

    if intent == "schools_far_from_hospitals":
        return await schools_far_from_hospitals(
            distance_meters=distance_meters if distance_meters is not None else 10000
        )

    if intent == "facilities_without_road_access":
        return await facilities_no_road_access(
            distance_meters=distance_meters if distance_meters is not None else 500
        )

    if intent == "facilities_without_fiber":
        return await facilities_without_fiber()

    if intent == "counties_without_electricity":
        return await counties_without_electricity()

    if intent == "wards_highest_population":
        return await wards_highest_population()

    if intent == "wards_lowest_population":
        return await wards_lowest_population()

    if intent == "counties_highest_population":
        return await counties_highest_population()

    if intent == "counties_lowest_population":
        return await counties_lowest_population()

    if intent == "hospitals_per_10000":
        return await counties_hospital_population_ratio()

    if intent == "schools_per_10000":
        return await counties_school_population_ratio()

    if intent == "high_population_wards_without_hospitals":
        return await high_population_wards_without_hospitals()

    if intent == "high_population_wards_without_major_facilities":
        return await high_population_wards_without_major_facilities()

    raise ValueError(f"Unsupported analysis intent: {intent}")


@router.get("/count/{dataset_name}")
async def dataset_count(dataset_name: str):
    try:
        count = await get_dataset_count(dataset_name)

        return {
            "dataset": dataset_name,
            "count": count,
        }

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )


@router.post("/ask", response_model=AnalysisResponse)
async def ask_question(request: QuestionRequest):
    question = request.question.strip()

    if not question:
        return AnalysisResponse(
            message="Please enter a spatial analysis question.",
            geojson={
                "type": "FeatureCollection",
                "features": [],
            },
        )

    try:
        ai_intent = await interpret_question(question)

        print("AI interpretation:", ai_intent.model_dump())

        if ai_intent.intent == "unsupported":
            return AnalysisResponse(
                message=(
                    "Please insert a predefined analysis. Thankyou"
                ),
                geojson={
                    "type": "FeatureCollection",
                    "features": [],
                },
            )

        return await execute_analysis(
            intent=ai_intent.intent,
            distance_meters=ai_intent.distance_meters,
            limit=ai_intent.limit,
        )

    except ValueError as error:
        print("Analysis value error:", repr(error))

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except Exception as error:
        print("Analysis error:", repr(error))

        raise HTTPException(
            status_code=500,
            detail="Failed to perform spatial analysis.",
        )