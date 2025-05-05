# dynamic versioning
from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("sen2sr")
except PackageNotFoundError:
    # package is not installed
    __version__ = "unknown"

