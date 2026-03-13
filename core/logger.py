import logging
from contextvars import ContextVar

request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)
user_id_var: ContextVar[str | None] = ContextVar("user_id", default=None)


class StringFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        request_id = request_id_var.get()
        user_id = user_id_var.get()

        parts = [
            f"time={self.formatTime(record, self.datefmt)}",
            f"level={record.levelname}",
            f"logger={record.name}",
            f"msg=\"{record.getMessage()}\"",
        ]

        if request_id:
            parts.append(f"request_id={request_id}")

        if user_id:
            parts.append(f"user_id={user_id}")

        if record.exc_info:
            parts.append(f"exception=\"{self.formatException(record.exc_info)}\"")

        for key, val in record.__dict__.items():
            if key not in logging.LogRecord.__dict__ and not key.startswith("_"):
                parts.append(f"{key}={val}")

        return " ".join(parts)


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(StringFormatter())

        logger.handlers = [handler]
        logger.setLevel(logging.INFO)

    return logger


logger = get_logger("app")