import json
from contextlib import contextmanager
from pathlib import Path
from typing import Optional, TypeVar, Generic, Generator, Type


from simple_state_tracker.data_model import DataModel
from simple_state_tracker.key_model import KeyModel

K = TypeVar("K", bound=KeyModel)
V = TypeVar("V", bound=DataModel)

class SimpleStateTracker(Generic[K, V]):
    def __init__(self, key_model: Type[K], data_model: Type[V], path: str):
        if not isinstance(key_model, type):
            raise TypeError("key_model must be a class, not an instance")

        if not isinstance(data_model, type):
            raise TypeError("data_model must be a class, not an instance")

        if not issubclass(key_model, KeyModel):
            raise TypeError("key_model must be a subclass of KeyModel")

        if not issubclass(data_model, DataModel):
            raise TypeError("data_model must be a subclass of DataModel")

        self.data_model = data_model
        self.key_model = key_model
        self.path = Path(path)
        self.data: dict[K, V] = {}
        self.load()

    def get(self, key: K) -> Optional[V]:
        """
        Get an entry as a pydantic model
        :param key:
        :return:
        """
        return self.data.get(key)

    def all(self) -> dict[K, V]:
        """
        Get all entries
        :return:
        """
        return {k: v.model_copy() for k, v in self.data.items()}

    def set(self, key: K, value: V) -> None:
        """
        Set an entry
        :param key:
        :param value:
        :return:
        """
        self.data[key] = value

    @contextmanager
    def edit(self, key: K) -> Generator[V, None, None]:
        """
        Yields an entry that can be edited, and is then saved
        :param key:
        :return:
        """
        instance = self.data.get(key, self.data_model())
        yield instance
        self.data[key] = instance

    def save(self):
        """
        Save data to file
        :return:
        """
        serializable_data = {
            str(k): v.model_dump(mode="json") for k, v in self.data.items()
        }
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(
                obj=serializable_data,
                fp=f,
                indent=2,
                sort_keys=True
            )

    def load(self):
        """
        Load data from file
        :return:
        """
        if self.path.exists():
            with open(self.path, "r", encoding="utf-8") as f:
                raw = json.load(f)
            self.data = {
                self.key_model.from_str(k): self.data_model(**v)
                for k, v in raw.items()
            }
        else:
            self.data = {}