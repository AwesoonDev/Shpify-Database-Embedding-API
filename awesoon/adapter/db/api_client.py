from typing import List

import requests

from awesoon.adapter.db.client import DatabaseClient
from awesoon.core.models.doc import Doc


class DatabaseApiClient(DatabaseClient):

    @classmethod
    def add_doc(cls, scan_id, doc: Doc):
        doc_data = doc.to_dict()
        return cls._make_request(requests.post, f"scans/{scan_id}/docs", json=doc_data)

    @classmethod
    def update_doc(self, doc: Doc):
        doc_data = doc.to_dict()
        return self._make_request(requests.put, f"docs/{doc.id}", json=doc_data)

    @classmethod
    def remove_doc(self, doc_id):
        return self._make_request(requests.delete, f"docs/{doc_id}")
