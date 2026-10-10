"""Application composition root for vehicle-sales."""

from collections.abc import Callable
from contextlib import asynccontextmanager

import httpx2
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy import Engine, create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from src.adapters.controllers.payment_controller import create_payment_router
from src.adapters.controllers.sale_controller import create_sale_router
from src.adapters.controllers.vehicle_controller import create_vehicle_router
from src.application.exceptions.vehicle_catalog_exceptions import (
    VehicleCatalogUnavailableError,
)
from src.application.interfaces.sale_repository import SaleRepository
from src.application.interfaces.vehicle_catalog import VehicleCatalog
from src.application.use_case.list_vehicles import (
    ListAvailableVehiclesUseCase,
    ListSoldVehiclesUseCase,
)
from src.application.use_case.process_payment import ProcessPaymentUseCase
from src.application.use_case.purchase_vehicle import PurchaseVehicleUseCase
from src.infra.database.base import Base
from src.infra.database.models import sale as _sale_model  # noqa: F401
from src.infra.database.repositories.sale_repository import SqlAlchemySaleRepository
from src.infra.http.vehicle_core_client import VehicleCoreClient
from src.infra.logging.formatter import LogConfig


logger = LogConfig(service_name="vehicle-sales", environment="local").get_logger()


def _prepare_schema(engine: Engine) -> None:
    try:
        Base.metadata.create_all(engine)
        logger.info("database_schema_ready")
    except SQLAlchemyError as error:
        logger.error("database_schema_failed", extra={"error": str(error)})


def create_app(
    sale_repository: SaleRepository | None = None,
    vehicle_catalog: VehicleCatalog | None = None,
) -> FastAPI:
    """Create the API with either real or test dependencies."""

    lifespan = None
    session_factory: Callable[[], Session] | None = None

    if sale_repository is None or vehicle_catalog is None:
        from src.infra.settings import Settings

        settings = Settings()
        engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
        session_factory = sessionmaker(bind=engine, expire_on_commit=False)
        http_client = httpx2.Client(
            base_url=settings.VEHICLE_CORE_URL,
            timeout=settings.VEHICLE_CORE_TIMEOUT_SECONDS,
        )
        sale_repository = sale_repository or SqlAlchemySaleRepository(session_factory)
        vehicle_catalog = vehicle_catalog or VehicleCoreClient(http_client)

        @asynccontextmanager
        async def lifespan(_: FastAPI):
            _prepare_schema(engine)
            yield
            http_client.close()

    app = FastAPI(title="vehicle-sales", lifespan=lifespan)

    @app.exception_handler(SQLAlchemyError)
    async def database_error_handler(_: Request, error: SQLAlchemyError) -> JSONResponse:
        logger.error("database_request_failed", extra={"error": str(error)})
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"detail": "Database unavailable."},
        )

    @app.exception_handler(VehicleCatalogUnavailableError)
    async def catalog_error_handler(_: Request, error: VehicleCatalogUnavailableError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"detail": "Vehicle catalog unavailable."},
        )

    @app.get("/health", tags=["health"])
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/health/ready", tags=["health"])
    def readiness() -> dict[str, str]:
        if session_factory is None:
            return {"status": "ok", "database": "not_configured"}
        try:
            with session_factory() as session:
                session.connection()
        except SQLAlchemyError as error:
            logger.warning("database_readiness_failed", extra={"error": str(error)})
            return {"status": "unavailable", "database": "unavailable"}
        return {"status": "ok", "database": "ok"}

    app.include_router(
        create_vehicle_router(
            ListAvailableVehiclesUseCase(vehicle_catalog, sale_repository),
            ListSoldVehiclesUseCase(vehicle_catalog),
        )
    )
    app.include_router(create_sale_router(PurchaseVehicleUseCase(sale_repository, vehicle_catalog)))
    app.include_router(create_payment_router(ProcessPaymentUseCase(sale_repository, vehicle_catalog)))
    return app


app = create_app()
