"""Frontend for Music Assistant."""
from pathlib import Path

__version__ = "0.0.66"

def where() -> Path:
    """Return path to the frontend."""
    return Path(__file__).parent
