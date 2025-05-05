import json

from pydantic import BaseModel


class KeyModel(BaseModel):
    """
    The model class used for the keys in the SimpleStateTracker
    Keys must serialize to a string and be hashable
    """

    def __str__(self) -> str:
        """Return a string version of this key for use in JSON serialization."""
        return json.dumps(self.model_dump(mode="json"))

    def __hash__(self):
        return hash(tuple(getattr(self, field) for field in self.model_fields))

    class Config:
        frozen = True
        extra = "forbid"

    @classmethod
    def from_str(cls, s: str) -> "KeyModel":
        return cls(**json.loads(s))