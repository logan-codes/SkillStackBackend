import logging

class StringFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        parts = [
            f"time:{self.formatTime(record, self.datefmt)}",
            f"level:{record.levelname}",
            f"logger:{record.name}",
            f"msg:\"{record.getMessage()}\"",
        ]

        if record.exc_info:
            parts.append(f"exception:\"{self.formatException(record.exc_info)}\"")

        for key, val in record.__dict__.items():
            if key not in logging.LogRecord.__dict__ and not key.startswith("_"):
                parts.append(f"{key}={val}")

        return " ".join(parts)


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)

    if not logger.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(StringFormatter())
        file_handler = logging.FileHandler("app.log")
        file_handler.setFormatter(StringFormatter())   
        logger.addHandler(console_handler) 
        logger.addHandler(file_handler) 
        logger.setLevel(logging.INFO)

    return logger


logger = get_logger("app")