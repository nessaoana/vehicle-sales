"""Use case for buying a vehicle."""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
import logging
from uuid import uuid4

from src.application.exceptions.vehicle_catalog_exceptions import (
    VehicleNotAvailableError,
    VehicleNotFoundError,
)
from src.application.interfaces.sale_repository import SaleRepository
from src.application.interfaces.vehicle_catalog import VehicleCatalog
from src.domain.entitites.car_sales import CarSale


logger = logging.getLogger("vehicle-sales")


@dataclass(frozen=True)
class PurchaseVehicleInput:
    """Input required to buy a vehicle."""

    vehicle_id: int
    buyer_cpf: str
    sale_date: date | None = None


class PurchaseVehicleUseCase:
    """Reserve an available vehicle with a pending sale awaiting payment."""

    def __init__(
        self,
        repository: SaleRepository,
        catalog: VehicleCatalog,
        payment_code_factory: Callable[[], str] = lambda: uuid4().hex,
        today: Callable[[], date] = date.today,
    ) -> None:
        self._repository = repository
        self._catalog = catalog
        self._payment_code_factory = payment_code_factory
        self._today = today

    def execute(self, data: PurchaseVehicleInput) -> CarSale:
        vehicle = self._catalog.get(data.vehicle_id)
        if vehicle is None:
            raise VehicleNotFoundError(data.vehicle_id)
        if vehicle.status != "available":
            raise VehicleNotAvailableError(data.vehicle_id)

        sale = self._repository.create(
            CarSale(
                vehicle_id=vehicle.id,
                buyer_cpf=data.buyer_cpf,
                sale_date=data.sale_date or self._today(),
                price=vehicle.price,
                payment_code=self._payment_code_factory(),
            )
        )
        logger.info(
            "vehicle_reserved_for_sale",
            extra={"sale_id": sale.id, "vehicle_id": sale.vehicle_id},
        )
        return sale
