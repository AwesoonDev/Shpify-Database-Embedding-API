from typing import List

import requests

from awesoon.core.adapter.db_client import DatabaseClient
from awesoon.core.exceptions import ShopInstallationNotFoundError
from awesoon.core.models.doc import Doc
from awesoon.core.models.shop import Shop


class DatabaseApiClient(DatabaseClient):

    @classmethod
    def get_shop(cls, shop_id):
        return cls._make_request(requests.get, f"shops/{shop_id}")

    @classmethod
    def get_shop_docs(cls, shop_id) -> List[Doc]:
        docs = cls._make_request(requests.get, f"shops/{shop_id}/docs")
        return [Doc(**doc) for doc in docs]

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

    @classmethod
    def get_shop_installation(cls, shop_id, app_name) -> Shop:
        installations = cls._make_request(requests.get, f"shops/{shop_id}/shopify-installations", params={"app_name": app_name})
        if installations:
            installation = installations[0]
            return Shop(
                shop_url=installation["shop_url"],
                access_token=installation["access_token"]
            )
        else:
            raise ShopInstallationNotFoundError
