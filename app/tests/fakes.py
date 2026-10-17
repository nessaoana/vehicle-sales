from decimal import Decimal

from src.application.exceptions.sale_exceptions import VehicleAlreadyReservedError
from src.application.exceptions.vehicle_catalog_exceptions import (
    VehicleCatalogUnavailableError,
)
from src.application.interfaces.vehicle_catalog import VehicleSearchFilters
from src.domain.entitites.car_sales import CarSale
from src.domain.entitites.vehicle import Vehicle


class InMemorySaleRepository:
    def __init__(self) -> None:
        self.sales: list[CarSale] = []

    def create(self, sale: CarSale) -> CarSale:
        if sale.vehicle_id in self.reserved_vehicle_ids():
            raise VehicleAlreadyReservedError(sale.vehicle_id)
        created = sale.model_copy(update={"id": len(self.sales) + 1})
        self.sales.append(created)
        return created

    def find_by_payment_code(self, payment_code: str) -> CarSale | None:
        return next((sale for sale in self.sales if sale.payment_code == payment_code), None)

    def update(self, sale: CarSale) -> CarSale:
        self.sales = [sale if current.id == sale.id else current for current in self.sales]
        return sale

    def reserved_vehicle_ids(self) -> set[int]:
        return {
            sale.vehicle_id
            for sale in self.sales
            if sale.sale_status in {"pending", "confirmed"}
        }


class InMemoryVehicleCatalog:
    def __init__(self, vehicles: list[Vehicle]) -> None:
        self.vehicles = {vehicle.id: vehicle for vehicle in vehicles}
        self.searches: list[tuple[str, VehicleSearchFilters]] = []

    def search(self, status: str, filters: VehicleSearchFilters) -> list[Vehicle]:
        self.searches.append((status, filters))
        matches = [vehicle for vehicle in self.vehicles.values() if vehicle.status == status]
        return sorted(matches, key=lambda vehicle: vehicle.price)

    def get(self, vehicle_id: int) -> Vehicle | None:
        return self.vehicles.get(vehicle_id)

    def mark_as_sold(self, vehicle_id: int) -> None:
        self.vehicles[vehicle_id] = self.vehicles[vehicle_id].model_copy(update={"status": "sold"})


class UnavailableVehicleCatalog:
    def search(self, status: str, filters: VehicleSearchFilters) -> list[Vehicle]:
        raise VehicleCatalogUnavailableError("connection refused")

    def get(self, vehicle_id: int) -> Vehicle | None:
        raise VehicleCatalogUnavailableError("connection refused")

    def mark_as_sold(self, vehicle_id: int) -> None:
        raise VehicleCatalogUnavailableError("connection refused")


def vehicle(vehicle_id: int, price: str, status: str = "available") -> Vehicle:
    return Vehicle(
        id=vehicle_id,
        brand="Toyota",
        model="Corolla",
        year=2022,
        color="Black",
        price=Decimal(price),
        status=status,
    )
