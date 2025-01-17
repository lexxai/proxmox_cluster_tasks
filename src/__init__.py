try:
    from __version__ import __version__
except ImportError:
    __version__ = "0.0.1"

__version_info__ = tuple(int(x) for x in __version__.split("."))
