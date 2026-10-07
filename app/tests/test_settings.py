from src.infra.settings import Settings


def test_settings_loads_defaults() -> None:
    settings = Settings(DATABASE_URL="sqlite:///vehicle_sales.db")

    assert settings.DATABASE_URL == "sqlite:///vehicle_sales.db"
    assert settings.POSTGRES_DB == "vehicle_sales"
    assert settings.AWS_DEFAULT_REGION == "us-east-1"
    assert settings.DEBUG is False
