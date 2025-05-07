from importlib.metadata import version

from .compose_app import AppFactory, compose_app
from .config import Config
from .connector import Connector
from .logging import create_logger
from .publisher import Publisher

__version__ = version("unitelabs_cdk")
__all__ = ["AppFactory", "Config", "Connector", "Publisher", "__version__", "compose_app", "create_logger"]
