import json
from decimal import Decimal

import httpx2
import pytest

from src.application.exceptions.vehicle_catalog_exceptions import (
    VehicleCatalogUnavailableError,
)
from src.application.interfaces.vehicle_catalog import VehicleSearchFilters
from src.infra.http.vehicle_core_client import VehicleCoreClient


CORE_VEHICLE = {
    "id": 1,
    "license_plate": "ABC1D23",
    "brand": "Toyota",
    "model": "Corolla",
    "year": 2022,
    "price": "90000.00",
    "color": "Black",
    "notes": None,
    "status": "available",
    "active": True,
}


def client_for(handler) -> VehicleCoreClient:
    http_client = httpx2.Client(base_url="http://core", transport=httpx2.MockTransport(handler))
    return VehicleCoreClient(http_client)


def test_search_sends_status_and_only_given_filters() -> None:
    requests: list[httpx2.Request] = []

    def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        return httpx2.Response(200, json=[CORE_VEHICLE])

    vehicles = client_for(handler).search(
        "available",
        VehicleSearchFilters(brand="toyota", min_year=2020),
    )

    assert requests[0].url.path == "/vehicles"
    assert dict(requests[0].url.params) == {
        "status": "available",
        "brand": "toyota",
        "min_year": "2020",
    }
    assert len(vehicles) == 1
    assert vehicles[0].id == 1
    assert vehicles[0].model == "Corolla"


def test_search_raises_when_core_answers_with_error() -> None:
    client = client_for(lambda request: httpx2.Response(500))

    with pytest.raises(VehicleCatalogUnavailableError):
        client.search("sold", VehicleSearchFilters())


def test_search_raises_when_core_is_unreachable() -> None:
    def handler(request: httpx2.Request) -> httpx2.Response:
        raise httpx2.ConnectError("connection refused", request=request)

    with pytest.raises(VehicleCatalogUnavailableError):
        client_for(handler).search("available", VehicleSearchFilters())


def test_get_returns_vehicle_or_none_when_missing() -> None:
    def handler(request: httpx2.Request) -> httpx2.Response:
        if request.url.path == "/vehicles/1":
            return httpx2.Response(200, json=CORE_VEHICLE)
        return httpx2.Response(404, json={"detail": "Vehicle not found"})

    client = client_for(handler)

    assert client.get(1).price == Decimal("90000.00")
    assert client.get(2) is None


def test_get_raises_when_core_answers_with_error() -> None:
    with pytest.raises(VehicleCatalogUnavailableError):
        client_for(lambda request: httpx2.Response(503)).get(1)


def test_mark_as_sold_patches_core_availability() -> None:
    requests: list[httpx2.Request] = []

    def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        return httpx2.Response(200, json={**CORE_VEHICLE, "status": "sold", "active": False})

    client_for(handler).mark_as_sold(1)

    assert requests[0].method == "PATCH"
    assert requests[0].url.path == "/vehicles/1/availability"
    assert json.loads(requests[0].content) == {"status": "sold", "active": False}
