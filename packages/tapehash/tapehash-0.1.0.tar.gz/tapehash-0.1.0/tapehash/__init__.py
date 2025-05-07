from .algos import tapehash1, tapehash2, tapehash3, license
from .work import (
    HasNonceProtocol,
    calculate_difficulty,
    calculate_target,
    check_difficulty,
    work
)
del algos

__version__ = '0.1.0'

def version() -> str:
    """Returns the current library version."""
    return __version__

