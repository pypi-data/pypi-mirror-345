import shlex
import subprocess
from collections.abc import Callable
from typing import Literal

from collection_sync import ReadWriteCollection
from collection_sync.util import identity_func


class IPRoute(ReadWriteCollection):
    def __init__(
        self,
        *,
        via: str | None = None,
        dev: str | None = None,
        table: str | None = None,
        scope: str | None = None,
        family_flag: Literal['', '-4', '-6'] = '',
    ):
        self.via = via
        self.dev = dev
        self.table = table
        self.scope = scope
        self.family_flag = family_flag

    def __iter__(self):
        cmd = self.build_cmd('show')
        for line in subprocess.check_output(cmd, shell=True, text=True).splitlines():
            yield line.strip()

    def add(self, item: str) -> None:
        subprocess.run(self.build_cmd('add', item), shell=True, check=True)

    def add_batch(self, items: list[str]) -> None:
        cmd = '; '.join(self.build_cmd('add', item) for item in items)
        subprocess.check_call(cmd, shell=True)

    def delete_by_key(self, key: str, key_func: Callable = identity_func) -> None:
        for item in self:
            if key_func(item) == key:
                subprocess.run(self.build_cmd('del', item), shell=True, check=True)
                break

    def delete_by_key_batch(self, keys: list[str], key_func: Callable = identity_func) -> None:
        _keys_set = set(keys)
        _items = [item for item in self if key_func(item) in _keys_set]
        cmd = '; '.join(self.build_cmd('del', item) for item in _items)
        subprocess.check_call(cmd, shell=True)

    def build_cmd(self, action: Literal['add', 'del', 'show'], route: str | None = None) -> str:
        if action == 'show' and route is not None:
            raise ValueError('route should be None when action is "show"')
        if action in {'add', 'del'} and route is None:
            raise ValueError('route should not be None when action is "add" or "del"')

        cmd = ['ip']
        if self.family_flag:
            cmd.append(self.family_flag)
        cmd += ['route', action]
        if route:
            cmd.append(route)
        if self.via:
            cmd += ['via', self.via]
        if self.dev:
            cmd += ['dev', self.dev]
        if self.table:
            cmd += ['table', self.table]
        if self.scope:
            cmd += ['scope', self.scope]
        return shlex.join(cmd)
