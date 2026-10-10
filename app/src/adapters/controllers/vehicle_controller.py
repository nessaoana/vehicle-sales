"""HTTP controller for vehicle listings."""

from typing import Annotated

from fastapi import APIRouter, Query

from src.adapters.schemas.vehicle import VehicleListQuery, VehicleResponse
from src.application.interfaces.vehicle_catalog import VehicleSearchFilters
from src.application.use_case.list_vehicles import (
    ListAvailableVehiclesUseCase,
    ListSoldVehiclesUseCase,
)


def create_vehicle_router(
    list_available_use_case: ListAvailableVehiclesUseCase,
    list_sold_use_case: ListSoldVehiclesUseCase,
) -> APIRouter:
    """Build the vehicle listing routes with injected use cases."""

    router = APIRouter(prefix="/vehicles", tags=["vehicles"])

    @router.get("/available")
    def list_available(filters: Annotated[VehicleListQuery, Query()]) -> list[VehicleResponse]:
        vehicles = list_available_use_case.execute(VehicleSearchFilters(**filters.model_dump()))
        return [VehicleResponse.model_validate(vehicle) for vehicle in vehicles]

    @router.get("/sold")
    def list_sold(filters: Annotated[VehicleListQuery, Query()]) -> list[VehicleResponse]:
        vehicles = list_sold_use_case.execute(VehicleSearchFilters(**filters.model_dump()))
        return [VehicleResponse.model_validate(vehicle) for vehicle in vehicles]

    return router
