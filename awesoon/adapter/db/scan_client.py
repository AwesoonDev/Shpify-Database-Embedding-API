
from typing import List

import requests

from awesoon.adapter.db.client import DatabaseClient
from awesoon.core.models.doc import Doc
from awesoon.core.models.scan import Scan, ScanStatus


class DatabaseScanClient(DatabaseClient):

    @classmethod
    def post_new_scan(cls, scan: Scan) -> str:
        scan_data = scan.to_dict()
        return cls._make_request(requests.post, "scans", json=scan_data)

    @classmethod
    def get_scan_docs(cls, scan_id) -> List[Doc]:
        result = []
        page = 0
        while True:
            docs = cls._make_request(requests.get, f"scans/{scan_id}/docs", params={"offset": page}, headers={'X-fields': '{id, hash, doc_type, doc_identifier}'})
            if not docs:
                break
            result.extend([Doc.from_dict(doc) for doc in docs])
            page += 1
        return result

    @classmethod
    def get_scan(self, scan_id) -> Scan:
        scan_data = self._make_request(requests.get, f"scans/{scan_id}")
        return Scan.from_dict(scan_data)

    @classmethod
    def update_scan_status(cls, scan: Scan, scan_status: ScanStatus):
        return cls._make_request(requests.put, f"scans/{scan.id}/status", json={"status": scan_status.value})
