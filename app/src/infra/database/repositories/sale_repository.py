"""SQLAlchemy implementation of the sale persistence port."""

from collections.abc import Callable
import logging

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.application.exceptions.sale_exceptions import (
    SaleNotFoundError,
    VehicleAlreadyReservedError,
)
from src.domain.entitites.car_sales import CarSale
from src.infra.database.mappers.sale_mapper import SaleMapper
from src.infra.database.models.sale import SaleModel


logger = logging.getLogger("vehicle-sales")


class SqlAlchemySaleRepository:
    """Persist sales using SQLAlchemy sessions."""

    def __init__(self, session_factory: Callable[[], Session]) -> None:
        self._session_factory = session_factory

    def create(self, sale: CarSale) -> CarSale:
        with self._session_factory() as session:
            model = SaleMapper.to_model(sale)
            session.add(model)
            try:
                session.commit()
            except IntegrityError as error:
                session.rollback()
                logger.warning(
                    "sale_persistence_rejected_reserved_vehicle",
                    extra={"vehicle_id": sale.vehicle_id},
                )
                raise VehicleAlreadyReservedError(sale.vehicle_id) from error
            session.refresh(model)
            return SaleMapper.to_entity(model)

    def find_by_payment_code(self, payment_code: str) -> CarSale | None:
        with self._session_factory() as session:
            model = session.query(SaleModel).filter_by(payment_code=payment_code).first()
            return SaleMapper.to_entity(model) if model else None

    def update(self, sale: CarSale) -> CarSale:
        if sale.id is None:
            raise SaleNotFoundError("Sale ID is required for update")
        with self._session_factory() as session:
            model = session.get(SaleModel, sale.id)
            if model is None:
                raise SaleNotFoundError(sale.id)
            for field, value in sale.model_dump(exclude={"id"}).items():
                setattr(model, field, value)
            session.commit()
            session.refresh(model)
            return SaleMapper.to_entity(model)
