"""Application exceptions related to the vehicle-core catalog."""


class VehicleCatalogUnavailableError(Exception):
    """Raised when vehicle-core cannot be reached or answers with an error."""
