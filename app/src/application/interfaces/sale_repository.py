"""Persistence port for vehicle sales."""

from typing import Protocol

from src.domain.entitites.car_sales import CarSale


class SaleRepository(Protocol):
    """Port used by application services to persist sales."""

    def create(self, sale: CarSale) -> CarSale:
        """Persist and return a sale."""

    def find_by_payment_code(self, payment_code: str) -> CarSale | None:
        """Return a sale by its payment code."""

    def update(self, sale: CarSale) -> CarSale:
        """Update and return an existing sale."""
