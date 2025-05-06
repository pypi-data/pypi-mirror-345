from importlib.metadata import version
from .api import EazyrentSDK
from . import utils


__version__ = version("eazyrent")

__all__ = ["EazyrentSDK", "utils"]
