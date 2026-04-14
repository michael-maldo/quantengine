import logging
import json
from datetime import datetime, timezone


class JsonFormatter(logging.Formatter):
    def format(self, record):
        # Base log structure
        log_record = {
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "level": record.levelname,
            "message": record.getMessage(),
        }

        # Reserved attributes from logging module (do NOT include)
        reserved = {
            "name", "msg", "args", "levelname", "levelno",
            "pathname", "filename", "module", "exc_info",
            "exc_text", "stack_info", "lineno", "funcName",
            "created", "msecs", "relativeCreated",
            "thread", "threadName", "processName", "process",
            "taskName"
        }

        # 🔥 Include ALL extra fields dynamically
        for key, value in record.__dict__.items():
            if key not in reserved and key not in log_record:
                log_record[key] = value

        return json.dumps(log_record)


def get_logger(name="quantengine"):
    logger = logging.getLogger(name)

    if not logger.handlers:  # prevent duplicate handlers
        logger.setLevel(logging.INFO)

        stream_handler = logging.StreamHandler()
        file_handler = logging.FileHandler("logs/ingestion.log")

        formatter = JsonFormatter()

        stream_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)

        logger.addHandler(stream_handler)
        logger.addHandler(file_handler)

    return logger





















# import logging
# import json
# from datetime import datetime, timezone

# class JsonFormatter(logging.Formatter):
#     def format(self, record):
#         log_record = {
#             "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
#             "level": record.levelname,
#             "message": record.getMessage(),
#         }

#         # include extra fields
#         if hasattr(record, "event"):
#             log_record["event"] = record.event

#         if hasattr(record, "symbol"):
#             log_record["symbol"] = record.symbol

#         if hasattr(record, "provider"):
#             log_record["provider"] = record.provider

#         if hasattr(record, "error"):
#             log_record["error"] = record.error

#         return json.dumps(log_record)

# def get_logger(name="quantengine"):
#     logger = logging.getLogger(name)

#     if not logger.handlers:  # prevent duplicate handlers
#         logger.setLevel(logging.INFO)

#         stream_handler = logging.StreamHandler()
#         file_handler = logging.FileHandler("logs/ingestion.log")

#         # formatter = logging.Formatter(
#         #     "[%(asctime)s] [%(levelname)s] %(message)s",
#         #     datefmt="%Y-%m-%d %H:%M:%S"
#         # )

#         file_handler.setFormatter(JsonFormatter())
#         stream_handler.setFormatter(JsonFormatter())

#         logger.addHandler(file_handler)
#         logger.addHandler(stream_handler)

#     return logger