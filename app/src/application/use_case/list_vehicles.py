"""Use cases for listing vehicles for sale and sold vehicles."""

from src.application.interfaces.sale_repository import SaleRepository
from src.application.interfaces.vehicle_catalog import VehicleCatalog, VehicleSearchFilters
from src.domain.entitites.vehicle import Vehicle


class ListAvailableVehiclesUseCase:
    """List vehicles that can be bought, cheapest first."""

    def __init__(self, catalog: VehicleCatalog, repository: SaleRepository) -> None:
        self._catalog = catalog
        self._repository = repository

    def execute(self, filters: VehicleSearchFilters) -> list[Vehicle]:
        vehicles = self._catalog.search("available", filters)
        reserved = self._repository.reserved_vehicle_ids()
        return [vehicle for vehicle in vehicles if vehicle.id not in reserved]


class ListSoldVehiclesUseCase:
    """List sold vehicles, cheapest first."""

    def __init__(self, catalog: VehicleCatalog) -> None:
        self._catalog = catalog

    def execute(self, filters: VehicleSearchFilters) -> list[Vehicle]:
        return self._catalog.search("sold", filters)
