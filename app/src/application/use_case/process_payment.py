"""Use case for handling payment notifications."""

import logging

from src.application.exceptions.sale_exceptions import (
    PaymentAlreadyProcessedError,
    SaleNotFoundError,
)
from src.application.interfaces.sale_repository import SaleRepository
from src.application.interfaces.vehicle_catalog import VehicleCatalog
from src.domain.entitites.car_sales import CarSale


logger = logging.getLogger("vehicle-sales")

SALE_STATUS_BY_PAYMENT_STATUS = {"paid": "confirmed", "cancelled": "cancelled"}


class ProcessPaymentUseCase:
    """Confirm or cancel a pending sale from the payment provider notification."""

    def __init__(self, repository: SaleRepository, catalog: VehicleCatalog) -> None:
        self._repository = repository
        self._catalog = catalog

    def execute(self, payment_code: str, payment_status: str) -> CarSale:
        sale = self._repository.find_by_payment_code(payment_code)
        if sale is None:
            raise SaleNotFoundError(payment_code)
        if sale.payment_status == payment_status:
            return sale
        if sale.payment_status != "pending":
            raise PaymentAlreadyProcessedError(payment_code)

        if payment_status == "paid":
            # Mark the vehicle first so a core failure leaves the sale pending
            # and the provider can retry the notification.
            self._catalog.mark_as_sold(sale.vehicle_id)

        updated = self._repository.update(
            sale.model_copy(
                update={
                    "payment_status": payment_status,
                    "sale_status": SALE_STATUS_BY_PAYMENT_STATUS[payment_status],
                }
            )
        )
        logger.info(
            "sale_payment_processed",
            extra={"sale_id": updated.id, "payment_status": payment_status},
        )
        return updated
