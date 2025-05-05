"""
simple_state_tracker: A minimal, file-backed state tracker using typed Pydantic models.

Key components:
- SimpleStateTracker: the tracker class
- KeyModel: base class for structured keys
- DataModel: base class for structured value records
"""

from .simple_state_tracker import SimpleStateTracker
from .key_model import KeyModel
from .data_model import DataModel

__all__ = ["SimpleStateTracker", "KeyModel", "DataModel"]