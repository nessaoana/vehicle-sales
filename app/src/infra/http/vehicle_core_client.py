"""HTTP client for the vehicle-core API."""

import logging

import httpx2

from src.application.exceptions.vehicle_catalog_exceptions import (
    VehicleCatalogUnavailableError,
)
from src.application.interfaces.vehicle_catalog import VehicleSearchFilters
from src.domain.entitites.vehicle import Vehicle


logger = logging.getLogger("vehicle-sales")


class VehicleCoreClient:
    """Implement the vehicle catalog port with HTTP calls to vehicle-core."""

    def __init__(self, http_client: httpx2.Client) -> None:
        self._http = http_client

    def search(self, status: str, filters: VehicleSearchFilters) -> list[Vehicle]:
        params = {
            "status": status,
            "brand": filters.brand,
            "model": filters.model,
            "min_year": filters.min_year,
            "max_year": filters.max_year,
        }
        response = self._request(
            "GET",
            "/vehicles",
            params={key: value for key, value in params.items() if value is not None},
        )
        return [Vehicle.model_validate(item) for item in response.json()]

    def get(self, vehicle_id: int) -> Vehicle | None:
        response = self._request("GET", f"/vehicles/{vehicle_id}", allow_not_found=True)
        if response.status_code == httpx2.codes.NOT_FOUND:
            return None
        return Vehicle.model_validate(response.json())

    def _request(
        self,
        method: str,
        path: str,
        *,
        allow_not_found: bool = False,
        **kwargs: object,
    ) -> httpx2.Response:
        try:
            response = self._http.request(method, path, **kwargs)
            if allow_not_found and response.status_code == httpx2.codes.NOT_FOUND:
                return response
            response.raise_for_status()
        except httpx2.HTTPError as error:
            logger.exception(
                "vehicle_core_request_failed",
                extra={"method": method, "path": path, "error": str(error)},
            )
            raise VehicleCatalogUnavailableError(str(error)) from error
        return response
