"""Vehicle as seen by the sales service."""

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class Vehicle(BaseModel):
    """Vehicle data owned by vehicle-core and read over HTTP."""

    model_config = ConfigDict(frozen=True, extra="ignore")

    id: int = Field(description="Vehicle identifier in vehicle-core.")
    brand: str | None = Field(default=None, description="Vehicle brand.")
    model: str = Field(description="Vehicle model name.")
    year: int = Field(description="Vehicle manufacturing year.")
    color: str | None = Field(default=None, description="Vehicle exterior color.")
    price: Decimal = Field(description="Vehicle sale price.")
    status: str = Field(description="Vehicle availability status in vehicle-core.")
