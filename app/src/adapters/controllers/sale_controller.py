"""HTTP controller for vehicle sales."""

from fastapi import APIRouter, HTTPException, status

from src.adapters.schemas.sale import PurchaseRequest, SaleResponse
from src.application.exceptions.sale_exceptions import VehicleAlreadyReservedError
from src.application.exceptions.vehicle_catalog_exceptions import (
    VehicleNotAvailableError,
    VehicleNotFoundError,
)
from src.application.use_case.purchase_vehicle import (
    PurchaseVehicleInput,
    PurchaseVehicleUseCase,
)


VEHICLE_NOT_AVAILABLE_DETAIL = "Vehicle is not available for sale."


def create_sale_router(purchase_use_case: PurchaseVehicleUseCase) -> APIRouter:
    """Build the sale routes with injected use cases."""

    router = APIRouter(prefix="/sales", tags=["sales"])

    @router.post("", status_code=status.HTTP_201_CREATED)
    def purchase_vehicle(payload: PurchaseRequest) -> SaleResponse:
        try:
            sale = purchase_use_case.execute(PurchaseVehicleInput(**payload.model_dump()))
        except VehicleNotFoundError as error:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found") from error
        except (VehicleNotAvailableError, VehicleAlreadyReservedError) as error:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=VEHICLE_NOT_AVAILABLE_DETAIL) from error
        return SaleResponse.model_validate(sale)

    return router
