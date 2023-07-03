
from pydoc import Doc
from typing import List

import requests

from awesoon.core.adapter.db_client import DatabaseClient
from awesoon.core.models.scan import Scan, ScanStatus


class DatabaseScanClient(DatabaseClient):

    @classmethod
    def post_new_scan(cls, scan: Scan) -> str:
        scan_data = scan.to_dict()
        return cls._make_request(requests.post, "scans", json=scan_data)

    @classmethod
    def get_scan_docs(cls, scan_id) -> List[Doc]:
        docs = cls._make_request(requests.get, f"scans/{scan_id}/docs", headers={'X-fields': '{id, hash, doc_type, doc_identifier}'})
        return [Doc(**doc) for doc in docs]

    @classmethod
    def get_scan(self, scan_id) -> Scan:
        scan_data = self._make_request(requests.get, f"scans/{scan_id}")
        return Scan(**{f: scan_data.get(f) for f in Scan.__annotations__})

    @classmethod
    def update_scan_status(cls, scan: Scan, scan_status: ScanStatus):
        return cls._make_request(requests.put, f"scans/{scan.id}/status", json={"status": scan_status.value})
