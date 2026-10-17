"""Port used to read and update vehicles owned by vehicle-core."""

from dataclasses import dataclass
from typing import Protocol

from src.domain.entitites.vehicle import Vehicle


@dataclass(frozen=True)
class VehicleSearchFilters:
    """Optional criteria used to search vehicles."""

    brand: str | None = None
    model: str | None = None
    min_year: int | None = None
    max_year: int | None = None


class VehicleCatalog(Protocol):
    """Access to the vehicle catalog kept by vehicle-core."""

    def search(self, status: str, filters: VehicleSearchFilters) -> list[Vehicle]:
        """Return vehicles with the given status, ordered by price ascending."""
