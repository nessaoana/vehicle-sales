"""Application exceptions related to vehicle sales."""


class SaleNotFoundError(Exception):
    """Raised when a requested sale does not exist."""


class VehicleAlreadyReservedError(Exception):
    """Raised when a vehicle already has a pending or confirmed sale."""
