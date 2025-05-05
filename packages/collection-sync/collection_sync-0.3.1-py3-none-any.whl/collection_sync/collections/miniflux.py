import operator
import os
from collections.abc import Callable

import miniflux

from collection_sync import ReadWriteCollection


class MinifluxCategoryFeeds(ReadWriteCollection):
    def __init__(
        self,
        category_id: int,
    ):
        self.client = miniflux.Client(os.environ['MINIFLUX_URL'], api_key=os.environ['MINIFLUX_API_KEY'])
        self.category_id = category_id
        self.feed_url_to_feed_id = {feed['feed_url']: feed['id'] for feed in self}
        self.feed_id_to_feed_url = {id_: url for url, id_ in self.feed_url_to_feed_id.items()}

    def __iter__(self):
        return iter(self.client.get_category_feeds(self.category_id))

    def add(self, item: str) -> None:
        feed_url = item
        feed_id = self.client.add_feed(feed_url, category_id=self.category_id)
        self.feed_url_to_feed_id[feed_url] = feed_id
        self.feed_id_to_feed_url[feed_id] = feed_url

    def delete_by_key(self, key: str, key_func: Callable = operator.itemgetter('feed_url')):
        feed_url = key
        for item in self:
            if key_func(item) == feed_url:
                feed_id = self.feed_url_to_feed_id[feed_url]
                self.client.delete_feed(feed_id)
                del self.feed_url_to_feed_id[feed_url]
                del self.feed_id_to_feed_url[feed_id]
                return
