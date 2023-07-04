from typing import List

import requests

from awesoon.adapter.db.client import DatabaseClient
from awesoon.core.exceptions import ShopInstallationNotFoundError
from awesoon.core.models.doc import Doc
from awesoon.core.models.shop import Shop


class DatabaseShopClient(DatabaseClient):

    @classmethod
    def get_shop(cls, shop_id):
        return cls._make_request(requests.get, f"shops/{shop_id}")

    @classmethod
    def get_shop_docs(cls, shop_id) -> List[Doc]:
        docs = cls._make_request(requests.get, f"shops/{shop_id}/docs")
        return [Doc.from_dict(doc) for doc in docs]

    @classmethod
    def get_shop_installation(cls, shop_id, app_name) -> Shop:
        installations = cls._make_request(requests.get, f"shops/{shop_id}/shopify-installations", params={"app_name": app_name})
        if installations:
            installation = installations[0]
            return Shop.from_dict(installation)
        else:
            raise ShopInstallationNotFoundError
