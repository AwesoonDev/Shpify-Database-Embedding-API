

from abc import ABC
import hashlib
import json
from typing import List
from awesoon.core.db_client import DatabaseApiClient
from awesoon.core.embedding import Embedder
from awesoon.core.filter import ResourceFilter
from awesoon.core.models.doc import Doc
from awesoon.core.models.shop import Shop

db_client = DatabaseApiClient()


class Resource(ABC):
    def __init__(self, raw, docs=None) -> None:
        self._raw = raw
        self._hash = self.set_hash()
        self._docs: List[Doc] = docs
        self._shop: Shop = None

    def parse(self: "Resource") -> "Resource":
        self._docs = [
            Doc(document=self._raw, hash=self.get_hash())
        ]
        return self

    def embed(self: "Resource") -> "Resource":
        if self._docs:
            return Embedder.embed_resource(self)
        return self

    def store(self, scan_id: str):
        for doc in self._docs:
            if doc.storage_status == "POST":
                db_client.add_doc(scan_id, doc)
            if doc.storage_status == "PUT":
                db_client.update_doc(doc)

    def delete(self):
        for doc in self._docs:
            db_client.remove_doc(doc.id)

    def apply_filter(self, filter: ResourceFilter) -> "Resource":
        return filter.filter(self)

    def raw(self):
        return self._raw

    def docs(self) -> List[Doc]:
        return self._docs

    def set_docs(self, docs: List[Doc]):
        self._docs = docs

    def get_hash(self):
        return self._hash

    def set_hash(self):
        to_hash = json.dumps(self._raw)
        hasher = hashlib.sha256()
        hasher.update(to_hash.encode())
        return hasher.hexdigest()

    def get_shop(self):
        return self._shop

    def set_shop(self, shop):
        self._shop = shop
