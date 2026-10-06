"""Domain entity for a vehicle sale."""

from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class CarSale(BaseModel):
    """Representa uma venda de veículo sem preocupações de persistência."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        populate_by_name=True,
    )

    id: int | None = Field(default=None, description="Unique sale identifier.")
    vehicle_id: int = Field(
        alias="vehicleId",
        description="Identifier of the sold vehicle.",
    )
    buyer_cpf: str = Field(description="CPF of the buyer.")
    sale_date: date = Field(description="Date on which the sale was created.")
    price: Decimal = Field(description="Sale price.")
    payment_code: str = Field(description="Payment provider transaction code.")
    payment_status: Literal["pending", "paid", "cancelled"] = Field(
        default="pending",
        description="Current payment status.",
    )
    sale_status: Literal["pending", "confirmed", "cancelled"] = Field(
        default="pending",
        description="Current sale status.",
    )