# backend/schemas/responses.py

from typing import Optional

from pydantic import BaseModel, Field


class AIIntent(BaseModel):
    """
    Structured interpretation returned by the AI model.
    """

    intent: str

    distance_meters: Optional[float] = Field(
        default=None,
        description="Distance threshold converted to meters."
    )

    limit: Optional[int] = Field(
        default=None,
        description="Optional number of results requested."
    )


class AnalysisResponse(BaseModel):
    message: str
    geojson: dict