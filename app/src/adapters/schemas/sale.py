"""HTTP schemas for vehicle sales."""

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.domain.validators.cpf import normalize_cpf


class PurchaseRequest(BaseModel):
    """Payload accepted by the purchase endpoint."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"vehicle_id": 1, "buyer_cpf": "529.982.247-25", "sale_date": "2026-10-10"}
            ]
        }
    )

    vehicle_id: int = Field(gt=0)
    buyer_cpf: str = Field(min_length=11, max_length=14)
    sale_date: date | None = Field(default=None, description="Defaults to today.")

    @field_validator("buyer_cpf")
    @classmethod
    def validate_cpf(cls, value: str) -> str:
        return normalize_cpf(value)


class SaleResponse(BaseModel):
    """Sale returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: int | None
    vehicle_id: int
    buyer_cpf: str
    sale_date: date
    price: Decimal
    payment_code: str
    payment_status: str
    sale_status: str
