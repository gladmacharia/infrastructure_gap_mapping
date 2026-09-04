import asyncio

from fastapi import APIRouter

from backend.services.map_service import get_dataset_count


router = APIRouter(
    prefix="/api/dashboard",
    tags=["Dashboard"],
)


@router.get("/summary")
async def dashboard_summary():

    dataset_names = [
        "counties",
        "schools",
        "hospitals",
        "police",
        "roads",
        "fiber",
        "electricity",
    ]

    counts = await asyncio.gather(
        *(get_dataset_count(name) for name in dataset_names)
    )

    return {
        "counties": counts[0],
        "schools": counts[1],
        "hospitals": counts[2],
        "police": counts[3],
        "roads": counts[4],
        "fiber": counts[5],
        "electricity": counts[6],
    }