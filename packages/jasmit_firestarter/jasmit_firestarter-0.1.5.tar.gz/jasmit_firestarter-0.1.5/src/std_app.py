"""
std_app.py
"""

import configparser

#  from .std_logging import StdLogging, function_logger
from std_logging import StdLogging, function_logger


#  =============================================================================
class StdApp:
    #  -----------------------------------------------------------------------------
    def __init__(self, app_name="", version="0.0.0") -> None:
        self._logger = StdLogging(f"logs/{app_name}.log")
        self._logger.info(f"Begin 'StdApp.__init__         ' arguments - ({app_name=}, {version=})")

        self._app_name = app_name
        #  self.__version__ = version

        self.cmdline_params = self.set_cmdline_params()
        self.cfg_file_params = self.set_cfg_file_params()

        self._logger.info("End   'StdApp.__init__         ' returns   - None\n")

    # ---------------------------------------------------------------------------------------------------------------------
    def __str__(self):
        return "StdApp"

    __repr__ = __str__

    #  -----------------------------------------------------------------------------
    @function_logger
    def set_cmdline_params(self):
        raise NotImplementedError("Please define set_cmdline_params in the derived class.")

    #  -----------------------------------------------------------------------------
    @function_logger
    def set_cfg_file_params(self):
        environment = self.cmdline_params.get("environment")

        cfgfile_path = self.cmdline_params.get("cfgfile")
        config = configparser.ConfigParser()
        with open(cfgfile_path) as file:
            config.read_file(file)

        return config[environment]
