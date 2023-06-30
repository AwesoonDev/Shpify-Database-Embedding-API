

from abc import ABC
import hashlib
import json
from typing import List, Optional
from awesoon.core.db_client import DatabaseApiClient
from awesoon.core.embedding import Embedder
from awesoon.core.exceptions import ResourceDocsHashError
from awesoon.core.models.doc import Doc
from awesoon.core.models.filter import FilterInterface
from awesoon.core.models.resource import ResourceInterface
from awesoon.core.models.scan import Scan
from awesoon.core.models.shop import Shop

db_client = DatabaseApiClient()


class Resource(ResourceInterface):
    def __init__(
            self,
            raw=None,
            docs: Optional[List[Doc]] = None,
            shop: Shop = None,
            enforce_hash: bool = True
    ) -> None:
        self._raw = raw
        self._hash = self.set_hash()
        self._docs: List[Doc] = docs
        self._shop: Shop = shop
        self._enforce_hash: bool = enforce_hash
        if self._docs is None:
            self.set_docs([])

    def identifier(self):
        return None

    def parse(self) -> "Resource":
        self._docs = [
            Doc(
                document=json.dumps(self._raw),
                hash=self.get_hash()
            )
        ]
        return self

    def embed(self: "Resource") -> "Resource":
        if self._docs:
            return Embedder.embed_resource(self)
        return self

    def execute(self, scan: Scan):
        if scan.docs is None:
            scan.docs = []
        for doc in self._docs:
            scan.docs.append(doc)

    def apply_filter(self, filter: FilterInterface) -> "Resource":
        return filter.filter(self)

    def raw(self):
        return self._raw

    def docs(self) -> List[Doc]:
        return self._docs

    def set_docs(self, docs: List[Doc]):
        for doc in docs:
            self.add_doc(doc)

    def add_doc(self, doc: Doc):
        if self._enforce_hash and doc.hash != self._hash:
            raise ResourceDocsHashError
        self._docs.append(doc)

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

    def set_storage_status(self, status: str):
        for doc in self._docs:
            doc.storage_status = status
