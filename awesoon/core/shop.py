from typing import List

from dotenv import load_dotenv

from awesoon.core import query_platforms
from awesoon.adapter.db.shop_client import DatabaseShopClient
from awesoon.core.models.shop import Shop
from awesoon.core.resource import Resource

load_dotenv()


def get_shop_policies(shop):
    # later we add the type of platform to the shop
    # and we do query[shop.platform] instead of query["shopify"]
    return query_platforms["shopify"]["querier"].get_shop_policies(shop.shop_url, shop.access_token)


def get_shop_products(shop):
    return query_platforms["shopify"]["querier"].get_shop_products(shop.shop_url, shop.access_token)


def get_shop_categories(shop):
    return query_platforms["shopify"]["querier"].get_shop_categories(shop.shop_url, shop.access_token)


def get_shop_orders(shop):
    return query_platforms["shopify"]["querier"].get_shop_orders(shop.shop_url, shop.access_token)


def get_shop_timezone(shop):
    return query_platforms["shopify"]["querier"].get_shop_timezone(shop.shop_url, shop.access_token)


def get_shop_resources(shop_id: int, app_name: str) -> list[Resource]:
    shop: Shop = DatabaseShopClient.get_shop_installation(shop_id, app_name)
    shop_resources: List[Resource] = []
    for query in query_platforms[shop.platform]["queries"]:
        shop_resources.extend(query(shop.shop_url, shop.access_token))
    for resource in shop_resources:
        resource.set_shop(shop)
    return shop_resources
