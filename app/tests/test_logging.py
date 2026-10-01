from src.infra.logging.formatter import DatadogLogConfig


def test_logger_is_configured_once() -> None:
    logger_config = DatadogLogConfig("vehicle-sales", "test")

    first_logger = logger_config.get_logger()
    second_logger = logger_config.get_logger()

    assert first_logger is second_logger
    assert first_logger.name == "vehicle-sales"
    assert len(first_logger.handlers) == 1
