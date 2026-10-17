from datetime import date

from fastapi.testclient import TestClient

from src.main import create_app
from tests.fakes import (
    InMemorySaleRepository,
    InMemoryVehicleCatalog,
    UnavailableVehicleCatalog,
    vehicle,
)


def client_with(*vehicles) -> TestClient:
    return TestClient(create_app(InMemorySaleRepository(), InMemoryVehicleCatalog(list(vehicles))))


def test_purchase_creates_pending_sale_with_core_price() -> None:
    client = client_with(vehicle(1, "90000.00"))

    response = client.post(
        "/sales",
        json={"vehicle_id": 1, "buyer_cpf": "529.982.247-25", "sale_date": "2026-10-10"},
    )

    body = response.json()
    assert response.status_code == 201
    assert body["vehicle_id"] == 1
    assert body["buyer_cpf"] == "52998224725"
    assert body["sale_date"] == "2026-10-10"
    assert body["price"] == "90000.00"
    assert body["payment_status"] == "pending"
    assert body["sale_status"] == "pending"
    assert len(body["payment_code"]) == 32


def test_purchase_defaults_sale_date_to_today() -> None:
    client = client_with(vehicle(1, "90000.00"))

    response = client.post("/sales", json={"vehicle_id": 1, "buyer_cpf": "52998224725"})

    assert response.json()["sale_date"] == date.today().isoformat()


def test_purchase_rejects_invalid_cpf() -> None:
    client = client_with(vehicle(1, "90000.00"))

    response = client.post("/sales", json={"vehicle_id": 1, "buyer_cpf": "123.456.789-00"})

    assert response.status_code == 422


def test_purchase_rejects_unknown_vehicle() -> None:
    client = client_with()

    response = client.post("/sales", json={"vehicle_id": 99, "buyer_cpf": "52998224725"})

    assert response.status_code == 404


def test_purchase_rejects_sold_or_reserved_vehicle() -> None:
    client = client_with(vehicle(1, "90000.00", status="sold"), vehicle(2, "70000.00"))

    sold_response = client.post("/sales", json={"vehicle_id": 1, "buyer_cpf": "52998224725"})
    first_response = client.post("/sales", json={"vehicle_id": 2, "buyer_cpf": "52998224725"})
    second_response = client.post("/sales", json={"vehicle_id": 2, "buyer_cpf": "52998224725"})

    assert sold_response.status_code == 409
    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json() == {"detail": "Vehicle is not available for sale."}


def test_purchase_returns_503_when_core_is_unavailable() -> None:
    client = TestClient(create_app(InMemorySaleRepository(), UnavailableVehicleCatalog()))

    response = client.post("/sales", json={"vehicle_id": 1, "buyer_cpf": "52998224725"})

    assert response.status_code == 503
