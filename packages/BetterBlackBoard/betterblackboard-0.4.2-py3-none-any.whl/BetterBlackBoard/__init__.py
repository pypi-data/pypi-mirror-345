import sys
if sys.version_info < (3, 11):
    try:
        import typing_extensions
    except ImportError:
        raise ImportError("Please install typing_extensions for Python < 3.11")
    del typing_extensions

from .cas import CASClient
from .bb import BlackBoard

__version__ = "0.3.0"
__all__ = ["CASClient", "BlackBoard"]