

from typing import List
from awesoon.core.db_client import DatabaseApiClient
from awesoon.core.exceptions import ResourceDocsHashError
from awesoon.core.models.doc import Doc
from awesoon.core.resource import Resource
from collections import defaultdict
from typing import List, DefaultDict

db_client = DatabaseApiClient()


class DocStore:
    def __init__(self, shop_id) -> None:
        self.shop_id = shop_id
        self._docs_store: dict[str, Resource] = self.setup_docs_store()
        self._removable_docs = []

    def get_docs_dict(self) -> dict[str, List[Doc]]:
        store: DefaultDict[str, List[Doc]] = defaultdict(list)
        docs = db_client.get_shop_docs(self.shop_id)
        for doc in docs:
            self._docs_store[doc.doc_identifier].append(doc)
        return dict(store)

    def setup_docs_store(self) -> dict[str, Resource]:
        docs_dict = self.get_docs_dict()
        store: DefaultDict[str, Resource] = defaultdict(Resource)
        for identifier, docs in docs_dict.items():
            try:
                store[identifier].set_docs(docs)
            except ResourceDocsHashError:
                self._removable_docs.extend(docs)
        return dict(store)

    def contains(self, doc_identifier):
        return doc_identifier in self._docs_store

    def get_removable_docs(self, include_unfiltered_docs=False):
        if include_unfiltered_docs:
            for _, resource in self._docs_store.items():
                self._removable_docs.extend(resource.docs())
        return self._removable_docs

    def add_to_removable_docs(self, identifier):
        resource: Resource = self._docs_store.pop(identifier, None)
        if resource:
            self._removable_docs.extend(resource.docs())

    def resource_exists_with_same_hash(self, resource: Resource):
        return self._docs_store[resource.identifier()].get_hash() == resource.get_hash()


class ResourceFilter:
    def __init__(self, shop_id) -> None:
        self.shop_id = shop_id
        self._store = DocStore()

    def filter(self, resource: Resource) -> Resource:
        if self._store.contains(resource.identifier()):
            if not self._store.resource_exists_with_same_hash(resource):
                resource.set_storage_status("POST")
                self._store.add_to_removable_docs(resource.identifier())
        else:
            resource.set_storage_status("POST")
        return resource

    def delete_docs(self, include_unfiltered_docs=True) -> Resource:
        docs = self._store.get_removable_docs(include_unfiltered_docs=include_unfiltered_docs)
        resource = Resource(
            docs=docs,
            enforce_hash=False
        )
        resource.set_storage_status("DELETE")
        return resource
