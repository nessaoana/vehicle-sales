"""SQLAlchemy model for vehicle sales."""

from datetime import date

from sqlalchemy import Date, Index, Integer, Numeric, String, text
from sqlalchemy.orm import Mapped, mapped_column

from src.infra.database.base import Base


ACTIVE_SALE_CONDITION = text("sale_status IN ('pending', 'confirmed')")


class SaleModel(Base):
    """Relational representation of a vehicle sale."""

    __tablename__ = "sales"
    __table_args__ = (
        # A vehicle can have only one pending or confirmed sale at a time.
        Index(
            "uq_sales_active_vehicle",
            "vehicle_id",
            unique=True,
            postgresql_where=ACTIVE_SALE_CONDITION,
            sqlite_where=ACTIVE_SALE_CONDITION,
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    vehicle_id: Mapped[int] = mapped_column(Integer, index=True)
    buyer_cpf: Mapped[str] = mapped_column(String(11))
    sale_date: Mapped[date] = mapped_column(Date)
    price: Mapped[float] = mapped_column(Numeric(12, 2))
    payment_code: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    payment_status: Mapped[str] = mapped_column(String(20), default="pending")
    sale_status: Mapped[str] = mapped_column(String(20), default="pending")
