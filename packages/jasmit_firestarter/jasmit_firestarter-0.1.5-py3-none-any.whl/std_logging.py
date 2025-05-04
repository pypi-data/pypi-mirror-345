"""
std_logging.py
"""

from logging import DEBUG, basicConfig, getLogger, shutdown


class StdLogging:
    #     _std_logger = None

    # ---------------------------------------------------------------------------------------------------------------------
    def __init__(self, log_name):
        basicConfig(
            level=DEBUG,
            filename=f"{log_name}",
            datefmt="%Y-%m-%d %H:%M:%S",
            format="%(asctime)s - %(levelname)s - %(message)s",
        )
        self._std_logger = getLogger()
        return None

    # ---------------------------------------------------------------------------------------------------------------------
    def __del__(self):
        shutdown()

    # ---------------------------------------------------------------------------------------------------------------------
    #  Define 5 helper short cuts to log at the 5 standard levels:
    #  debug = 10
    #  info = 20
    #  warn = 30
    #  error = 40
    #  exception = 40
    #  critical = 50
    def debug(self, message):
        self._std_logger.debug(message)
        return None

    def info(self, message):
        self._std_logger.info(message)
        return None

    def warning(self, message):
        self._std_logger.warning(message)
        return None

    def error(self, message):
        self._std_logger.error(message)
        return None

    def exception(self, message):
        self._std_logger.exception(message)
        return None

    def critical(self, message):
        self._std_logger.critical(message)
        return None


# ======================================================================================================================
def function_logger(func):
    def logged(*args, **kwargs):
        function_name = func.__name__.ljust(24)
        getLogger().info(f"Begin '{function_name}' arguments - {args} keyword arguments - {kwargs}")
        result = func(*args, **kwargs)
        getLogger().info(f"End   '{function_name}' returns   - {result}")
        return result

    return logged
