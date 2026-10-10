from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

from src.main import create_app


class UnusedSaleRepository:
    pass


def test_health_endpoints_without_database() -> None:
    client = TestClient(create_app(UnusedSaleRepository()))

    assert client.get("/health").json() == {"status": "ok"}
    assert client.get("/health/ready").json() == {"status": "ok", "database": "not_configured"}


def test_real_app_initializes_database_and_reports_readiness(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path / 'sales.db'}")

    with TestClient(create_app()) as client:
        response = client.get("/health/ready")

    assert response.json() == {"status": "ok", "database": "ok"}


def test_real_app_starts_without_database(monkeypatch, tmp_path) -> None:
    unreachable = tmp_path / "missing-dir" / "sales.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{unreachable}")

    with TestClient(create_app()) as client:
        health_response = client.get("/health")
        ready_response = client.get("/health/ready")

    assert health_response.status_code == 200
    assert ready_response.json() == {"status": "unavailable", "database": "unavailable"}


def test_database_errors_return_503() -> None:
    app = create_app(UnusedSaleRepository())

    @app.get("/boom")
    def boom() -> None:
        raise OperationalError("SELECT 1", {}, Exception("connection refused"))

    response = TestClient(app).get("/boom")

    assert response.status_code == 503
    assert response.json() == {"detail": "Database unavailable."}
