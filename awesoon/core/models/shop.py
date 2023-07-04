from dataclasses import dataclass
from awesoon.core.models import BaseDataClass


@dataclass
class Shop(BaseDataClass):
    shop_url: str
    access_token: str
    shop_id: int = None
    app_name: str = None
    platform: str = "shopify"
