import re
from collections.abc import Callable
from typing import Any

from collection_sync import ReadWriteCollection
from collection_sync.collections.list import List
from collection_sync.util import identity_func


class MarkdownLinksList(ReadWriteCollection):
    def __init__(self, file: str):
        self.file = file
        with open(file) as f:
            text = f.read()
        data = [
            {'title': title, 'url': url}
            for title, url in re.findall(r'\[(.+)\]\((.+)\)', text)
        ]
        self.data_list_collection = List(data)

    def __iter__(self):
        return iter(self.data_list_collection)

    def add(self, item: dict):
        self.data_list_collection.add(item)
        self.write_to_file()

    def delete_by_key(self, key: Any, key_func: Callable = identity_func):
        self.data_list_collection.delete_by_key(key, key_func)
        self.write_to_file()

    def write_to_file(self):
        with open(self.file, 'w') as f:
            for item in self:
                print(f'- [{item["title"]}]({item["url"]})', file=f)
