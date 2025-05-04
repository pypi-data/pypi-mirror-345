from pydantic import BaseModel, ConfigDict


class DataModel(BaseModel):
    """
    The base class for all value models used in SimpleStateTracker.
    Ensures strict schemas and type safety.
    """
    model_config = ConfigDict(
        extra="forbid",
        arbitrary_types_allowed=False,
        frozen=False  # Optional: enforce immutability if desired
    )

    def copy_with(self, **updates) -> "DataModel":
        """
        Return a new instance with the given fields updated.
        """
        return self.model_copy(update=updates)