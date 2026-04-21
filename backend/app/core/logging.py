import datetime
import json
import logging


class JsonFormatter(logging.Formatter):
    """
    Studio Standard JSON Formatter.
    Outputs logs in a structured format suitable for cloud logging aggregators.
    """

    def format(self, record: logging.LogRecord) -> str:
        log_obj = {
            "timestamp": datetime.datetime.fromtimestamp(
                record.created, tz=datetime.UTC
            ).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "funcName": record.funcName,
            "line": record.lineno,
        }

        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)

        # Include extra attributes if they are JSON serializable
        if hasattr(record, "extra") and isinstance(record.extra, dict):
            for key, value in record.extra.items():
                if key not in log_obj:
                    log_obj[key] = value

        return json.dumps(log_obj)


def setup_logging():
    """Initializes the structured logging system."""
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())

    root_logger = logging.getLogger()
    root_logger.handlers = [handler]
    root_logger.setLevel(logging.INFO)

    # Optional: Silence noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
