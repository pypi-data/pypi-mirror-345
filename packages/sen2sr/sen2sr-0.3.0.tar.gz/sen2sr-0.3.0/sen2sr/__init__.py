# dynamic versioning
from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("sen2sr")
except PackageNotFoundError:
    # package is not installed
    __version__ = "unknown"

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

# Optionally, you can add a message or logging
if not TORCH_AVAILABLE:
    print("SEN2SR: PyTorch is not available. Install it to use this package.")