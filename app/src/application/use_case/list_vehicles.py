"""Use cases for listing vehicles for sale and sold vehicles."""

from src.application.interfaces.vehicle_catalog import VehicleCatalog, VehicleSearchFilters
from src.domain.entitites.vehicle import Vehicle


class ListAvailableVehiclesUseCase:
    """List vehicles that can be bought, cheapest first."""

    def __init__(self, catalog: VehicleCatalog) -> None:
        self._catalog = catalog

    def execute(self, filters: VehicleSearchFilters) -> list[Vehicle]:
        return self._catalog.search("available", filters)


class ListSoldVehiclesUseCase:
    """List sold vehicles, cheapest first."""

    def __init__(self, catalog: VehicleCatalog) -> None:
        self._catalog = catalog

    def execute(self, filters: VehicleSearchFilters) -> list[Vehicle]:
        return self._catalog.search("sold", filters)
