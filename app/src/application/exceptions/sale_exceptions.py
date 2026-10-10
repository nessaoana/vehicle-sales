"""Application exceptions related to vehicle sales."""


class SaleNotFoundError(Exception):
    """Raised when a requested sale does not exist."""


class VehicleAlreadyReservedError(Exception):
    """Raised when a vehicle already has a pending or confirmed sale."""


class PaymentAlreadyProcessedError(Exception):
    """Raised when a payment notification contradicts an already processed payment."""
