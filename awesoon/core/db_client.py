import requests
from awesoon.config import config
from awesoon.core.exceptions import ShopInstallationNotFoundError
from awesoon.core.models.doc import doc
from copy import copy


class DatabaseApiClient:
    def __init__(self):
        self.config = config
        self.db_base_url = self.config.database.url_api_version

    def _gen_url(self, route):
        return f"{self.db_base_url}/{route}"

    def _make_request(self, method, route, **kwargs):
        response = method(self._gen_url(route), **kwargs)
        response.raise_for_status()
        return response.json()

    def get_shop(self, shop_id):
        return self._make_request(requests.get, f"shops/{shop_id}")

    def initiate_new_scan(self, shop_id):
        return self._make_request(requests.post, f"shops/{shop_id}/initiate_scan")

    def get_scan_hashes(self, scan_id):
        return self._make_request(requests.get, f"scans/{scan_id}/hashes")

    def add_doc(self, scan_id, doc: doc):
        doc_data = copy(doc.__dict__)
        return self._make_request(requests.post, f"scans/{scan_id}/docs", json=doc_data)

    def update_doc(self, scan_id, doc_id, doc: doc):
        doc_data = copy(doc.__dict__)
        doc_id = doc.identifier
        return self._make_request(requests.put, f"scans/{scan_id}/docs/{doc_id}", json=doc_data)

    def remove_doc(self, scan_id, doc_id):
        return self._make_request(requests.delete, f"scan/{scan_id}/docs/{doc_id}")

    def get_shop_installation(self, shop_id, app_name):
        installations = self._make_request(requests.get, f"shops/{shop_id}/shopify-installations", params={"app_name": app_name})
        if installations:
            return installations[0]
        else:
            raise ShopInstallationNotFoundError
