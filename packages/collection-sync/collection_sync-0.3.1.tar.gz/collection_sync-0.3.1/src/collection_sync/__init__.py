__version__ = '0.3.1'

import abc
import itertools
from collections.abc import Callable
from collections.abc import Iterable
from typing import Any

from collection_sync.util import identity_func


class ReadCollection(Iterable):
    def cache_items(self, key_func: Callable):
        self._cache = {key_func(item): item for item in self}  # pylint: disable=attribute-defined-outside-init

    def delete_cache(self):
        self._cache = None  # pylint: disable=attribute-defined-outside-init

    def contains_key(self, key: Any, key_func: Callable = identity_func) -> bool:
        try:
            self.get_by_key(key, key_func)
        except KeyError:
            return False
        return True

    def get_by_key(self, key: Any, key_func: Callable = identity_func):
        if hasattr(self, '_cache') and self._cache is not None:
            return self._cache[key]
        for x in self:
            if key_func(x) == key:
                return x
        raise KeyError(f'Key {key} not found')


class WriteCollection(abc.ABC):
    @abc.abstractmethod
    def add(self, item: Any): ...

    @abc.abstractmethod
    def delete_by_key(self, key: Any, key_func: Callable = identity_func): ...


class ReadWriteCollection(ReadCollection, WriteCollection):
    ...


def sync_collections(
    source: ReadCollection,
    destination: ReadWriteCollection,
    *,
    source_key: Callable = identity_func,
    destination_key: Callable = identity_func,
    source_destination_transform: Callable = identity_func,
    delete_missing: bool = False,
    batch_add: bool = False,
    batch_delete: bool = False,
    batch_size_add: int | None = None,
    batch_size_delete: int | None = None,
    cache_before_source: bool = True,
    cache_before_destination: bool = True,
    delete_cache_after_source: bool = False,
    delete_cache_after_destination: bool = False,
    dry_run: bool = False,
) -> tuple[int, int]:
    """
    delete_missing: bool
        If there are items in the destination that don't exist in the
        source and this is True, delete them. Otherwise, leave them alone.
    """
    if cache_before_source:
        source.cache_items(key_func=source_key)
    if cache_before_destination:
        destination.cache_items(key_func=destination_key)

    n_added = 0
    n_deleted = 0

    _add_items = []
    for item in source:
        key = source_key(item)
        if not destination.contains_key(key, key_func=destination_key):
            add_data = source_destination_transform(item)
            _add_items.append(add_data)

    if not _add_items:
        pass
    elif batch_add:
        if not hasattr(destination, 'add_batch'):
            raise ValueError('Destination collection does not support batch add')

        for batch in itertools.batched(_add_items, batch_size_add or len(_add_items)):
            print(f'ADD BATCH: {len(batch)} items')
            if dry_run:
                continue
            destination.add_batch(batch)
            n_added += len(batch)
    else:
        for add_data in _add_items:
            print(f'ADD: {add_data}')
            if dry_run:
                continue
            destination.add(add_data)
            n_added += 1

    if delete_missing:
        _delete_keys = []
        for item in destination:
            key = destination_key(item)
            if not source.contains_key(key, key_func=source_key):
                _delete_keys.append(key)

        if not _delete_keys:
            pass
        elif batch_delete:
            if not hasattr(destination, 'delete_by_key_batch'):
                raise ValueError('Destination collection does not support batch delete')

            for batch in itertools.batched(_delete_keys, batch_size_delete or len(_delete_keys)):
                print(f'DELETE BATCH: {len(batch)} items')
                if dry_run:
                    continue
                destination.delete_by_key_batch(batch)
                n_deleted += len(batch)
        else:
            for key in _delete_keys:
                print(f'DELETE {key}')
                if dry_run:
                    continue
                destination.delete_by_key(key, key_func=destination_key)
                n_deleted += 1

    if delete_cache_after_source:
        source.delete_cache()
    if delete_cache_after_destination:
        destination.delete_cache()

    return n_added, n_deleted
