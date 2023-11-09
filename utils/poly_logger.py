import sys
import logging
import logging.config
import logging.handlers
import os
import queue
from enum import Enum, auto

# Environment variable for JSON logging
JSON_LOGGING = os.environ.get("JSON_LOGGING", "false").lower() == "true"

# Define log levels
class LogLevel(Enum):
    DEBUG = auto()
    INFO = auto()
    WARNING = auto()
    ERROR = auto()
    CRITICAL = auto()

# Define log colors
class LogColor(Enum):
    RESET = "\033[0m"
    WHITE = "\033[37m"
    BLUE = "\033[34m"
    LIGHT_BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    ORANGE = "\033[33m"
    RED = "\033[91m"
    GREY = "\33[90m"

# Define log emojis
class LogEmoji(Enum):
    DEBUG = "🐛"
    INFO = "📝"
    WARNING = "⚠️"
    ERROR = "❌"
    CRITICAL = "💥"

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
        record.levelname = f"{LogColor[level.name].value}{record.levelname}{LogColor.RESET.value}"
        record.msg = f"{LogEmoji[level.name].value} {record.msg}"
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
