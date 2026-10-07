from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from src.domain.entitites.car_sales import CarSale


def test_car_sale_uses_pending_status_by_default() -> None:
    sale = CarSale(
        vehicle_id=10,
        buyer_cpf="12345678909",
        sale_date=date(2026, 10, 1),
        price=Decimal("75000.00"),
        payment_code="payment-123",
    )

    assert sale.id is None
    assert sale.payment_status == "pending"
    assert sale.sale_status == "pending"


def test_car_sale_serializes_its_fields() -> None:
    sale = CarSale(
        id=1,
        vehicle_id=10,
        buyer_cpf="12345678909",
        sale_date=date(2026, 10, 1),
        price=Decimal("75000.00"),
        payment_code="payment-123",
        payment_status="paid",
        sale_status="confirmed",
    )

    assert sale.model_dump() == {
        "id": 1,
        "vehicle_id": 10,
        "buyer_cpf": "12345678909",
        "sale_date": date(2026, 10, 1),
        "price": Decimal("75000.00"),
        "payment_code": "payment-123",
        "payment_status": "paid",
        "sale_status": "confirmed",
    }
    assert sale.model_dump(by_alias=True)["vehicleId"] == 10


def test_car_sale_accepts_vehicle_id_alias() -> None:
    sale = CarSale(
        vehicleId=10,
        buyer_cpf="12345678909",
        sale_date=date(2026, 10, 1),
        price=Decimal("75000.00"),
        payment_code="payment-123",
    )

    assert sale.vehicle_id == 10


def test_car_sale_rejects_extra_fields() -> None:
    invalid_data = {
        "vehicle_id": 10,
        "buyer_cpf": "12345678909",
        "sale_date": date(2026, 10, 1),
        "price": Decimal("75000.00"),
        "payment_code": "payment-123",
        "unexpected_field": "value",
    }

    with pytest.raises(ValidationError):
        CarSale(**invalid_data)


def test_car_sale_rejects_invalid_payment_status() -> None:
    invalid_data = {
        "vehicle_id": 10,
        "buyer_cpf": "12345678909",
        "sale_date": date(2026, 10, 1),
        "price": Decimal("75000.00"),
        "payment_code": "payment-123",
        "payment_status": "unknown",
    }

    with pytest.raises(ValidationError):
        CarSale(**invalid_data)


def test_car_sale_is_immutable() -> None:
    sale = CarSale(
        vehicle_id=10,
        buyer_cpf="12345678909",
        sale_date=date(2026, 10, 1),
        price=Decimal("75000.00"),
        payment_code="payment-123",
    )

    with pytest.raises(ValidationError):
        sale.sale_status = "confirmed"