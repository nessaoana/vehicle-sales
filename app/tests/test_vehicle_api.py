from decimal import Decimal

from fastapi.testclient import TestClient

from src.application.exceptions.vehicle_catalog_exceptions import (
    VehicleCatalogUnavailableError,
)
from src.application.interfaces.vehicle_catalog import VehicleSearchFilters
from src.domain.entitites.vehicle import Vehicle
from src.main import create_app


class InMemorySaleRepository:
    pass


class InMemoryVehicleCatalog:
    def __init__(self, vehicles: list[Vehicle]) -> None:
        self.vehicles = vehicles
        self.searches: list[tuple[str, VehicleSearchFilters]] = []

    def search(self, status: str, filters: VehicleSearchFilters) -> list[Vehicle]:
        self.searches.append((status, filters))
        matches = [vehicle for vehicle in self.vehicles if vehicle.status == status]
        return sorted(matches, key=lambda vehicle: vehicle.price)


class UnavailableVehicleCatalog:
    def search(self, status: str, filters: VehicleSearchFilters) -> list[Vehicle]:
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


def test_list_available_vehicles_returns_cheapest_first_and_forwards_filters() -> None:
    catalog = InMemoryVehicleCatalog(
        [vehicle(1, "90000.00"), vehicle(2, "70000.00"), vehicle(3, "50000.00", status="sold")]
    )
    client = TestClient(create_app(InMemorySaleRepository(), catalog))

    response = client.get(
        "/vehicles/available",
        params={"brand": "toyota", "model": "corolla", "min_year": 2020, "max_year": 2024},
    )

    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == [2, 1]
    assert response.json()[0] == {
        "id": 2,
        "brand": "Toyota",
        "model": "Corolla",
        "year": 2022,
        "color": "Black",
        "price": "70000.00",
    }
    assert catalog.searches == [
        ("available", VehicleSearchFilters(brand="toyota", model="corolla", min_year=2020, max_year=2024))
    ]


def test_list_sold_vehicles_returns_cheapest_first() -> None:
    catalog = InMemoryVehicleCatalog(
        [vehicle(1, "90000.00", status="sold"), vehicle(2, "70000.00", status="sold"), vehicle(3, "50000.00")]
    )
    client = TestClient(create_app(InMemorySaleRepository(), catalog))

    response = client.get("/vehicles/sold")

    assert [item["id"] for item in response.json()] == [2, 1]


def test_list_vehicles_rejects_inverted_year_range() -> None:
    client = TestClient(create_app(InMemorySaleRepository(), InMemoryVehicleCatalog([])))

    response = client.get("/vehicles/available", params={"min_year": 2024, "max_year": 2020})

    assert response.status_code == 422


def test_list_vehicles_returns_503_when_core_is_unavailable() -> None:
    client = TestClient(create_app(InMemorySaleRepository(), UnavailableVehicleCatalog()))

    response = client.get("/vehicles/sold")

    assert response.status_code == 503
    assert response.json() == {"detail": "Vehicle catalog unavailable."}
