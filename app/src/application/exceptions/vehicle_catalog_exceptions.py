"""Application exceptions related to the vehicle-core catalog."""


class VehicleCatalogUnavailableError(Exception):
    """Raised when vehicle-core cannot be reached or answers with an error."""


class VehicleNotFoundError(Exception):
    """Raised when vehicle-core does not know the requested vehicle."""


class VehicleNotAvailableError(Exception):
    """Raised when the requested vehicle is not available for sale."""
