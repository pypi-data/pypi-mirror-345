#  __init__.py
"""
Init file for the firestarter package.
This package contains the firestarter module, which is a Python
implementation of the firestarter tool.
The firestarter module provides a set of functions and classes
for creating and managing standard projects.
"""

#  Package level variables
__version__ = "0.1.5"
__author__ = "jasmit"

# Package level imports
from .std_app import StdApp
# from .std_dbconn import get_database_connection
# from .std_logging import StdLogging, function_logger
# from .std_report import StdReport

# __all__ = ['StdApp', 'get_database_connection', 'StdLogging', 'function_logger', 'StdReport']
__all__ = ['StdApp']
