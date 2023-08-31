

import hashlib
import json
from typing import List, Optional
from awesoon.core.embedding import Embedder
from awesoon.core.exceptions import ResourceDocsHashError
from awesoon.core.models.doc import Doc
from awesoon.core.models.doc_type_enums import StorageStatus
from awesoon.core.models.filter import FilterInterface
from awesoon.core.models.resource import ResourceInterface, ResourcesInterface
from awesoon.core.models.scan import Scan
from awesoon.core.models.shop import Shop

resource_hash_version = "1.0.0+"

class Resource(ResourceInterface):
    def __init__(
            self,
            raw=None,
            docs: Optional[List[Doc]] = None,
            shop: Shop = None,
            enforce_hash: bool = True
    ) -> None:
        self._raw = raw
        self.set_hash()
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
            Embedder.embed_resource(self)
        return self

    def save(self, scan: Scan, commit=False):
        self.execute(StorageStatus.ADD, scan, commit=commit)

    def delete(self, scan: Scan, commit=False):
        self.execute(StorageStatus.DELETE, scan, commit=commit)

    def execute(self, action: StorageStatus, scan: Scan, commit=False):
        if scan.docs is None:
            scan.docs = []
        for doc in self._docs:
            doc.storage_status = action
            scan.docs.append(doc)
        if commit:
            scan.commit()

    def apply_filter(self, filter: FilterInterface) -> "Resource":
        return filter.filter(self)

    def raw(self):
        return self._raw

    def docs(self) -> List[Doc]:
        return self._docs

    def set_docs(self, docs: List[Doc]):
        if docs:
            for doc in docs:
                self.add_doc(doc)
        else:
            self._docs = []

    def add_doc(self, doc: Doc):
        if self._enforce_hash:
            if self.get_hash() and doc.hash != self._hash:
                raise ResourceDocsHashError
            else:
                self.override_hash(doc.hash)
        self._docs.append(doc)

    def get_hash(self):
        return self._hash

    def set_hash(self):
        if self.raw():
            to_hash = json.dumps(self._raw)
            hasher = hashlib.sha256()
            hasher.update(to_hash.encode())
            hash = hasher.hexdigest()
            versioned_hash = f"{resource_hash_version}-{hash}"
            self._hash = versioned_hash
            
        else:
            self._hash = None

    def override_hash(self, hash):
        self._hash = hash

    def get_shop(self):
        return self._shop

    def set_shop(self, shop):
        self._shop = shop

    def set_storage_status(self, status: StorageStatus):
        for doc in self._docs:
            doc.storage_status = status


class Resources(ResourcesInterface):
    def __init__(
            self,
            resources: List[Resource] = None
    ) -> None:
        self.resources = resources or []

    def parse_all(self):
        for resource in self.resources:
            resource.parse()
        return self

    def apply_filter(self, filter):
        filtered_resources = []
        for resource in self.resources:
            filtered_resources.append(
                resource.apply_filter(filter)
            )
        self.resources = filtered_resources
        return self

    def embed_all(self):

        if self.resources:
            Embedder.embed_resources(self.resources)
        return self

    def save_all(self, scan: Scan, commit=False):
        for resource in self.resources:
            resource.save(scan, commit=commit)

    def delete_all(self, scan: Scan, commit=False):
        for resource in self.resources:
            resource.delete(scan, commit=commit)
