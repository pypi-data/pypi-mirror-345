from pydantic import BaseModel


class KeyModel(BaseModel):
    """
    The model class used for the keys in the SimpleStateTracker
    Keys must serialize to a string and be hashable
    """

    def __str__(self) -> str:
        """Return a string version of this key for use in JSON serialization."""
        return ":".join(str(getattr(self, field)) for field in self.model_fields)

    def __hash__(self):
        return hash(tuple(getattr(self, field) for field in self.model_fields))

    class Config:
        frozen = True
        extra = "forbid"

    @classmethod
    def from_str(cls, s: str) -> "KeyModel":
        parts = s.split(":")
        field_types = [f.annotation for f in cls.model_fields.values()]
        converted = [field_type(part) for field_type, part in zip(field_types, parts)]
        fields = cls.model_fields.keys()
        return cls(**dict(zip(fields, converted)))