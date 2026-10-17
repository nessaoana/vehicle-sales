"""Convert sales between the domain and SQLAlchemy representations."""

from src.domain.entitites.car_sales import CarSale
from src.infra.database.models.sale import SaleModel


class SaleMapper:
    """Keep persistence details out of the sale domain entity."""

    @staticmethod
    def to_model(sale: CarSale) -> SaleModel:
        """Convert a domain sale into a persistence model."""
        model_data = sale.model_dump(exclude={"id"})
        if sale.id is not None:
            model_data["id"] = sale.id
        return SaleModel(**model_data)

    @staticmethod
    def to_entity(model: SaleModel) -> CarSale:
        """Convert a persistence model into a domain sale."""
        return CarSale.model_validate(model, from_attributes=True)
