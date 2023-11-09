import sys
import logging
import logging.config
import logging.handlers
import os
import queue
from enum import Enum, auto

# Environment variable for JSON logging
JSON_LOGGING = os.environ.get("JSON_LOGGING", "false").lower() == "true"

class LogLevel(Enum):
    DEBUG = logging.DEBUG  # 10
    INFO = logging.INFO    # 20
    WARNING = logging.WARNING  # 30
    ERROR = logging.ERROR  # 40
    CRITICAL = logging.CRITICAL  # 50

# Define log colors
class LogColor(Enum):
    RESET = "\033[0m"      # Reset to default color
    DEBUG = "\033[34m"     # Blue
    INFO = "\033[32m"      # Green
    WARNING = "\033[33m"   # Yellow
    ERROR = "\033[31m"     # Red
    CRITICAL = "\033[35m"  # Magenta

# Define log emojis
class LogEmoji(Enum):
    DEBUG = "🐞"  # Bug emoji for debug
    INFO = "ℹ️"   # Information emoji for info
    WARNING = "⚠️"  # Warning emoji for warning
    ERROR = "❗"   # Exclamation mark emoji for error
    CRITICAL = "💥" # Explosion emoji for critical

class PolyLogger(logging.Logger):
    FORMAT: str = "%(asctime)s %(name)-15s %(levelname)-8s %(message)s"
    JSON_FORMAT: str = '{"time": "%(asctime)s", "name": "%(name)s", "level": "%(levelname)s", "message": "%(message)s"}'
    _instance = None  # Singleton instance

    def __new__(cls, name, level=logging.NOTSET):
        if cls._instance is None:
            cls._instance = super(PolyLogger, cls).__new__(cls)
        return cls._instance

    def __init__(self, name: str, level: str = "DEBUG"):
        if not hasattr(self, 'initialized'):  # Avoid re-initialization
            super().__init__(name, getattr(logging, level.upper()))
            self.initialized = True

            # Set up the handler with a queue
            queue_handler = logging.handlers.QueueHandler(queue.Queue(-1))
            formatter = logging.Formatter(self.JSON_FORMAT if JSON_LOGGING else self.FORMAT)
            queue_handler.setFormatter(formatter)
            self.addHandler(queue_handler)

            # Set up the console handler
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.addHandler(console_handler)

    def _format_record(self, record: logging.LogRecord, level: LogLevel) -> logging.LogRecord:
        if JSON_LOGGING:
            return record  # No special formatting for JSON output
        # Color and emoji formatting
        level_name = LogLevel(record.levelno).name  # Convert numeric level to enum name
        record.levelname = f"{LogColor[level_name].value}{record.levelname}{LogColor.RESET.value}"
        record.msg = f"{LogEmoji[level_name].value} {record.msg}"
        return record

    def _log(self, level, msg, args, exc_info=None, extra=None, stack_info=False):
        """
        Low-level logging routine which creates a LogRecord and then calls
        all the handlers of this logger to handle the record.
        """
        if self.isEnabledFor(level):
            # Find caller information if not provided
            fn, lno, func, sinfo = self.findCaller(stack_info, stacklevel=2)
            record = self.makeRecord(self.name, level, fn, lno, msg, args, exc_info, func, extra, sinfo)
            # Handle the record with the formatted message
            record = self._format_record(record, LogLevel(level))
            self.handle(record)

    def log(self, level, msg, *args, **kwargs):
        """
        Log 'msg % args' with the integer severity 'level'.
        """
        if not isinstance(level, int):
            if isinstance(level, Enum):
                level = level.value
            else:
                raise ValueError("level must be an integer or an Enum member")
        if self.isEnabledFor(level):
            self._log(level, msg, args, **kwargs)


# Add custom log level for chat if needed in future
# logging.addLevelName(LogLevel.CHAT.value, "CHAT")

# Singleton logger setup
logger = PolyLogger(__name__)

# Example usage:
# logger.info("This is an info message")
