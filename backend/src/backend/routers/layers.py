from fastapi import APIRouter, Depends, HTTPException

from backend.schemas.requests import BoundingBox

from backend.services.map_service import (
    get_layer_by_bbox,
)


router = APIRouter(
    prefix="/api/layers",
    tags=["Layers"],
)


@router.get("/{layer_name}")
async def get_layer(
    layer_name: str,
    bbox: BoundingBox = Depends(),
):

    try:
        return await get_layer_by_bbox(
            layer_name=layer_name,
            bbox=bbox,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve spatial layer.",
        )