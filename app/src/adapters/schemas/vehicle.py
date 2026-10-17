"""HTTP schemas for vehicle listings."""

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class VehicleListQuery(BaseModel):
    """Optional query filters for the vehicle listing endpoints."""

    model_config = ConfigDict(extra="forbid")

    brand: str | None = Field(default=None, max_length=80)
    model: str | None = Field(default=None, max_length=80)
    min_year: int | None = Field(default=None, ge=1886, le=2100)
    max_year: int | None = Field(default=None, ge=1886, le=2100)

    @model_validator(mode="after")
    def validate_year_range(self) -> "VehicleListQuery":
        if self.min_year is not None and self.max_year is not None and self.min_year > self.max_year:
            raise ValueError("min_year must be less than or equal to max_year")
        return self


class VehicleResponse(BaseModel):
    """Vehicle returned by the listing endpoints."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    brand: str | None
    model: str
    year: int
    color: str | None
    price: Decimal
