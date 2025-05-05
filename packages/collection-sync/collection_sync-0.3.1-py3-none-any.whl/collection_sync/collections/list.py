from collections.abc import Callable
from collections.abc import Iterator
from typing import Any

from collection_sync import ReadWriteCollection
from collection_sync.util import identity_func


class List(ReadWriteCollection):
    def __init__(self, data: list | None = None):
        self.data = [] if data is None else data

    def __iter__(self) -> Iterator:
        return iter(self.data)

    def add(self, item: Any):
        self.data.append(item)

    def delete_by_key(self, key: Any, key_func: Callable = identity_func):
        self.data = [
            item for item in self
            if key_func(item) != key
        ]
