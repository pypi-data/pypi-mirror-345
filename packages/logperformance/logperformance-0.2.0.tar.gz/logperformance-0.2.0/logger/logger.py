import logging
import colorlog
from typing import Callable, Any
from time import time, strftime
from os import getenv, path, makedirs, getcwd


class LogPerformance:
    """Class for logging performance and errors."""

    _instance = None
    initialized: bool = False

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(LogPerformance, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self) -> None:
        if hasattr(self, "initialized") and self.initialized:
            return

        handler = colorlog.StreamHandler()
        handler.setFormatter(
            colorlog.ColoredFormatter(
                "%(log_color)s%(asctime)s - "
                "%(name)s - %(levelname)s - "
                "%(message)s"
            )
        )

        logger = colorlog.getLogger(__name__)
        if (
            not logger.handlers and getenv("DEBUG_WRITE_FILE", "True") == "True"
        ):  # write file log
            log_directory = path.join(path.dirname(getcwd()), "log")
            self.create_directory(log_directory)
            log_filepath = path.join(log_directory, strftime("%d_%m_%Y_%H_%M") + ".log")

            file_handler = logging.FileHandler(log_filepath, encoding="utf-8")
            file_handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                )
            )
            logger.addHandler(handler)
            logger.addHandler(file_handler)

        log_system = getenv("LOG_LEVEL")
        logger.setLevel(logging.INFO if log_system is None else logging.DEBUG)
        if log_system == "DEBUG":
            logging.basicConfig()
            logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
        self.logger = logger
        self.log_messages = ""
        self.initialized = True

    @staticmethod
    def check_exists_directory(work_directory: str) -> bool:
        return path.exists(work_directory)

    @classmethod
    def create_directory(cls, work_directory: str) -> None:
        if not cls.check_exists_directory(work_directory):
            makedirs(work_directory)
            cls().info(f"Created directory {work_directory}")

    def log_performance(self, func: Callable) -> Callable:
        """Decorator to log the performance of a function."""

        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time()
            result = func(*args, **kwargs)
            end_time = time()
            msg = f"🙂 Function {func.__name__} args {str(args[1:])} took {round(end_time - start_time, 2)} seconds"
            self.logger.debug(msg)
            self._append_log_message(msg, logging.DEBUG)
            return result

        return wrapper

    def log_error(self, func: Callable) -> Callable:
        """Decorator to log errors in a function."""

        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                msg = f"❗ Error in {func.__name__}: {e}"
                self.logger.error(msg)
                self._append_log_message(msg, logging.ERROR)
                raise
            return result

        return wrapper

    def log_warning(self, func: Callable) -> Callable:
        """Decorator to log warnings in a function."""

        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time()
            result = func(*args, **kwargs)
            end_time = time()
            msg = f"🔔 Function {func.__name__} args {str(args[1:])} took {round(end_time - start_time, 2)} seconds"
            self.warning(msg)
            self._append_log_message(msg, logging.WARNING)
            return result

        return wrapper

    def info(self, msg: str) -> None:
        """Log an info message."""
        msg = "🙂 " + msg
        self.logger.info(msg)
        self._append_log_message(msg, logging.INFO)

    def warning(self, msg: str) -> None:
        """Log a warning message."""
        self.logger.warning(msg)
        self._append_log_message(msg, logging.WARNING)

    def error(self, msg: str) -> None:
        """Log an error message."""
        msg = "❗ " + msg
        self.logger.error(msg)
        self._append_log_message(msg, logging.ERROR)

    def _append_log_message(self, msg: str, level: int) -> None:
        """Append log message with timestamp and level."""
        is_log_level = getattr(self, "logger").level == 10
        is_run_debug = getenv("LOG_LEVEL") == "DEBUG"
        is_debug_function = level != 10
        if is_log_level and is_run_debug or is_debug_function:
            self.log_messages = msg
