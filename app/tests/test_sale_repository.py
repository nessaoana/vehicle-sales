from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.application.exceptions.sale_exceptions import (
    SaleNotFoundError,
    VehicleAlreadyReservedError,
)
from src.domain.entitites.car_sales import CarSale
from src.infra.database.base import Base
from src.infra.database.repositories.sale_repository import SqlAlchemySaleRepository


def build_repository() -> SqlAlchemySaleRepository:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, class_=Session, expire_on_commit=False)
    return SqlAlchemySaleRepository(session_factory)


def pending_sale(vehicle_id: int = 10, payment_code: str = "payment-123") -> CarSale:
    return CarSale(
        vehicle_id=vehicle_id,
        buyer_cpf="52998224725",
        sale_date=date(2026, 10, 1),
        price=Decimal("75000.00"),
        payment_code=payment_code,
    )


def test_sale_repository_creates_and_finds_by_payment_code() -> None:
    repository = build_repository()

    created = repository.create(pending_sale())
    found = repository.find_by_payment_code("payment-123")

    assert created.id is not None
    assert found == created
    assert repository.find_by_payment_code("unknown") is None


def test_sale_repository_updates_sale_status() -> None:
    repository = build_repository()
    created = repository.create(pending_sale())

    updated = repository.update(
        created.model_copy(update={"payment_status": "paid", "sale_status": "confirmed"})
    )

    assert updated.payment_status == "paid"
    assert updated.sale_status == "confirmed"
    assert repository.find_by_payment_code("payment-123") == updated


def test_sale_repository_rejects_second_active_sale_for_same_vehicle() -> None:
    repository = build_repository()
    repository.create(pending_sale())

    with pytest.raises(VehicleAlreadyReservedError):
        repository.create(pending_sale(payment_code="payment-456"))


def test_sale_repository_allows_new_sale_after_cancellation() -> None:
    repository = build_repository()
    created = repository.create(pending_sale())
    repository.update(
        created.model_copy(update={"payment_status": "cancelled", "sale_status": "cancelled"})
    )

    second = repository.create(pending_sale(payment_code="payment-456"))

    assert second.sale_status == "pending"


def test_sale_repository_rejects_missing_sales_on_update() -> None:
    repository = build_repository()

    with pytest.raises(SaleNotFoundError):
        repository.update(pending_sale().model_copy(update={"id": 999}))
    with pytest.raises(SaleNotFoundError):
        repository.update(pending_sale())


def test_sale_repository_lists_reserved_vehicle_ids() -> None:
    repository = build_repository()
    repository.create(pending_sale(vehicle_id=1, payment_code="payment-1"))
    confirmed = repository.create(pending_sale(vehicle_id=2, payment_code="payment-2"))
    cancelled = repository.create(pending_sale(vehicle_id=3, payment_code="payment-3"))
    repository.update(confirmed.model_copy(update={"payment_status": "paid", "sale_status": "confirmed"}))
    repository.update(cancelled.model_copy(update={"payment_status": "cancelled", "sale_status": "cancelled"}))

    assert repository.reserved_vehicle_ids() == {1, 2}
