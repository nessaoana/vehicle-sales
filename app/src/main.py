"""Application composition root for vehicle-sales."""

from collections.abc import Callable
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from src.application.interfaces.sale_repository import SaleRepository
from src.infra.database.base import Base
from src.infra.database.models import sale as _sale_model  # noqa: F401
from src.infra.database.repositories.sale_repository import SqlAlchemySaleRepository
from src.infra.logging.formatter import LogConfig


logger = LogConfig(service_name="vehicle-sales", environment="local").get_logger()


def create_app(sale_repository: SaleRepository | None = None) -> FastAPI:
    """Create the API with either real or test dependencies."""

    lifespan = None
    session_factory: Callable[[], Session] | None = None

    if sale_repository is None:
        from src.infra.settings import Settings

        settings = Settings()
        engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
        session_factory = sessionmaker(bind=engine, expire_on_commit=False)
        sale_repository = SqlAlchemySaleRepository(session_factory)

        @asynccontextmanager
        async def lifespan(_: FastAPI):
            try:
                Base.metadata.create_all(engine)
                logger.info("database_schema_ready")
            except SQLAlchemyError as error:
                logger.error("database_schema_failed", extra={"error": str(error)})
            yield

    app = FastAPI(title="vehicle-sales", lifespan=lifespan)

    @app.exception_handler(SQLAlchemyError)
    async def database_error_handler(_: Request, error: SQLAlchemyError) -> JSONResponse:
        logger.error("database_request_failed", extra={"error": str(error)})
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"detail": "Database unavailable."},
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

    return app


app = create_app()
