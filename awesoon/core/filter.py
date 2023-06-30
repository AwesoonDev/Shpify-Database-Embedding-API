

from typing import List
from awesoon.core.db_client import DatabaseApiClient
from awesoon.core.models.doc import Doc
from awesoon.core.resource import Resource

db_client = DatabaseApiClient()


class ResourceFilter:
    def __init__(self, shop_id) -> None:
        self.shop_id = shop_id
        self._docs_store: dict[str: Doc] = self.setup_docs_store()

    def filter(self, resource: Resource) -> Resource:
        for doc in resource.docs():
            if doc.doc_identifier in self._docs_store:
                if doc.hash != self._docs_store[doc.doc_identifier].hash:
                    doc.storage_status = "PUT"
                    doc.id = self._docs_store[doc.doc_identifier].id
                else:
                    doc.storage_status = "IGNORE"
                del self._docs_store[doc.doc_identifier]
            else:
                doc.storage_status = "POST"
        return resource

    def delete_docs(self) -> Resource:
        docs = self._docs_store.values()
        for doc in docs:
            doc.storage_status = "DELETE"
        return Resource(
            docs=docs
        )

    def setup_docs_store(self) -> Resource:
        docs = db_client.get_shop_docs(self.shop_id)
        return {
            doc.doc_identifier: doc for doc in docs
        }
