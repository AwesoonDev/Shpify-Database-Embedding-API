

from collections import defaultdict
from typing import DefaultDict, List

from awesoon.adapter.db_api_client import DatabaseApiClient
from awesoon.core.exceptions import ResourceDocsHashError
from awesoon.core.models.doc import Doc
from awesoon.core.models.doc_type_enums import StorageStatus
from awesoon.core.resource import Resource


class DocStore:
    def __init__(self, shop_id) -> None:
        self.shop_id = shop_id
        self._removable_docs = []
        self._docs_store: dict[str, Resource] = self.setup_docs_store()

    def get_docs_dict(self) -> dict[str, List[Doc]]:
        store: DefaultDict[str, List[Doc]] = defaultdict(list)
        docs = DatabaseApiClient.get_shop_docs(self.shop_id)
        for doc in docs:
            store[doc.doc_identifier].append(doc)
        return dict(store)

    def setup_docs_store(self) -> dict[str, Resource]:
        docs_dict = self.get_docs_dict()
        store: DefaultDict[str, Resource] = defaultdict(Resource)
        for identifier, docs in docs_dict.items():
            try:
                store[identifier].set_docs(docs)
            except ResourceDocsHashError:
                self._removable_docs.extend(docs)
                del store[identifier]
        return dict(store)

    def contains(self, doc_identifier):
        return doc_identifier in self._docs_store

    def get_removable_docs(self, include_unobserved_docs=False):
        if include_unobserved_docs:
            for _, resource in self._docs_store.items():
                self._removable_docs.extend(resource.docs())
        return self._removable_docs

    def add_to_removable_docs(self, resource: Resource):
        self._removable_docs.extend(resource.docs())

    def observe_resource_from_doc_store(self, resource: Resource):
        if resource.identifier() in self._docs_store:
            observed_resource: Resource = self._docs_store.pop(resource.identifier(), None)
            if observed_resource.get_hash() != resource.get_hash():
                self.add_to_removable_docs(observed_resource)
                return False
            else:
                return True
        return False


class ResourceFilter:
    def __init__(self, shop_id) -> None:
        self.shop_id = shop_id
        self._store = DocStore(shop_id=shop_id)

    def filter(self, resource: Resource) -> Resource:
        if not self._store.observe_resource_from_doc_store(resource):
            return resource
        return Resource()

    def removable_docs(self, include_unobserved_docs=True) -> Resource:
        docs = self._store.get_removable_docs(include_unobserved_docs=include_unobserved_docs)
        resource = Resource(
            docs=docs,
            enforce_hash=False
        )
        return resource
