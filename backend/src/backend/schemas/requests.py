from pydantic import BaseModel, Field, model_validator


class BoundingBox(BaseModel):
    min_lon: float = Field(..., ge=-180, le=180)
    min_lat: float = Field(..., ge=-90, le=90)
    max_lon: float = Field(..., ge=-180, le=180)
    max_lat: float = Field(..., ge=-90, le=90)
    limit: int = Field(default=5000, ge=1, le=10000)

    @model_validator(mode="after")
    def validate_bbox(self):
        if self.min_lon >= self.max_lon:
            raise ValueError("min_lon must be less than max_lon")

        if self.min_lat >= self.max_lat:
            raise ValueError("min_lat must be less than max_lat")

        return self

class QuestionRequest(BaseModel):
    question: str