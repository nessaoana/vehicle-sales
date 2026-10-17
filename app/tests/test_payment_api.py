from fastapi.testclient import TestClient

from src.application.exceptions.vehicle_catalog_exceptions import (
    VehicleCatalogUnavailableError,
)
from src.main import create_app
from tests.fakes import InMemorySaleRepository, InMemoryVehicleCatalog, vehicle


class FlakyVehicleCatalog(InMemoryVehicleCatalog):
    def __init__(self, vehicles) -> None:
        super().__init__(vehicles)
        self.core_down = False

    def mark_as_sold(self, vehicle_id: int) -> None:
        if self.core_down:
            raise VehicleCatalogUnavailableError("connection refused")
        super().mark_as_sold(vehicle_id)


def purchase(client: TestClient, vehicle_id: int = 1) -> str:
    response = client.post("/sales", json={"vehicle_id": vehicle_id, "buyer_cpf": "52998224725"})
    return response.json()["payment_code"]


def build(*vehicles) -> tuple[TestClient, FlakyVehicleCatalog]:
    catalog = FlakyVehicleCatalog(list(vehicles))
    return TestClient(create_app(InMemorySaleRepository(), catalog)), catalog


def test_paid_webhook_confirms_sale_and_marks_vehicle_as_sold() -> None:
    client, catalog = build(vehicle(1, "90000.00"))
    payment_code = purchase(client)

    response = client.post("/payments/webhook", json={"payment_code": payment_code, "status": "paid"})

    assert response.status_code == 200
    assert response.json()["payment_status"] == "paid"
    assert response.json()["sale_status"] == "confirmed"
    assert catalog.vehicles[1].status == "sold"
    assert [item["id"] for item in client.get("/vehicles/sold").json()] == [1]
    assert client.get("/vehicles/available").json() == []


def test_cancelled_webhook_cancels_sale_and_releases_vehicle() -> None:
    client, catalog = build(vehicle(1, "90000.00"))
    payment_code = purchase(client)

    response = client.post(
        "/payments/webhook",
        json={"payment_code": payment_code, "status": "cancelled"},
    )

    assert response.json()["payment_status"] == "cancelled"
    assert response.json()["sale_status"] == "cancelled"
    assert catalog.vehicles[1].status == "available"
    assert [item["id"] for item in client.get("/vehicles/available").json()] == [1]
    assert client.post("/sales", json={"vehicle_id": 1, "buyer_cpf": "52998224725"}).status_code == 201


def test_webhook_is_idempotent_and_rejects_contradicting_status() -> None:
    client, _ = build(vehicle(1, "90000.00"))
    payment_code = purchase(client)
    client.post("/payments/webhook", json={"payment_code": payment_code, "status": "paid"})

    repeated = client.post("/payments/webhook", json={"payment_code": payment_code, "status": "paid"})
    contradicting = client.post(
        "/payments/webhook",
        json={"payment_code": payment_code, "status": "cancelled"},
    )

    assert repeated.status_code == 200
    assert repeated.json()["sale_status"] == "confirmed"
    assert contradicting.status_code == 409


def test_webhook_rejects_unknown_payment_code_and_status() -> None:
    client, _ = build()

    unknown_code = client.post("/payments/webhook", json={"payment_code": "nope", "status": "paid"})
    unknown_status = client.post("/payments/webhook", json={"payment_code": "nope", "status": "refunded"})

    assert unknown_code.status_code == 404
    assert unknown_status.status_code == 422


def test_paid_webhook_keeps_sale_pending_when_core_is_down() -> None:
    client, catalog = build(vehicle(1, "90000.00"))
    payment_code = purchase(client)
    catalog.core_down = True

    failed = client.post("/payments/webhook", json={"payment_code": payment_code, "status": "paid"})
    catalog.core_down = False
    retried = client.post("/payments/webhook", json={"payment_code": payment_code, "status": "paid"})

    assert failed.status_code == 503
    assert retried.status_code == 200
    assert retried.json()["sale_status"] == "confirmed"
