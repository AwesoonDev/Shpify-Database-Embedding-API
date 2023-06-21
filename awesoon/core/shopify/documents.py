

from abc import ABC
import json


class ShopifyObject(ABC):
    def __init__(self, raw) -> None:
        self._raw = raw

    def process_document(self):
        pass

    def raw(self):
        return self._raw


class Policy(ShopifyObject):
    pass


class Product(ShopifyObject):
    pass


class Category(ShopifyObject):
    pass
