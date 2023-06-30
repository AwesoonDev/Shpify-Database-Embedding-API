from dataclasses import dataclass


@dataclass
class Shop:
    shop_url: str
    access_token: str
    shop_id: int = None
    app_name: str = None
    platform: str = "shopify"
