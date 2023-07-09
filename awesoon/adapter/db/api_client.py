from typing import List

import requests

from awesoon.adapter.db.client import DatabaseClient
from awesoon.core.models.doc import Doc


class DatabaseApiClient(DatabaseClient):

    @classmethod
    def add_docs(cls, scan_id, docs: List[Doc]):
        docs = [doc.to_dict() for doc in docs]
        return cls._make_request(requests.post, f"scans/{scan_id}/docs", json=docs)

    @classmethod
    def update_doc(self, doc: Doc):
        doc_data = doc.to_dict()
        return self._make_request(requests.put, f"docs/{doc.id}", json=doc_data)

    @classmethod
    def remove_docs(self, doc_ids: List[str]):
        return self._make_request(requests.delete, "docs", params={"id": doc_ids})
