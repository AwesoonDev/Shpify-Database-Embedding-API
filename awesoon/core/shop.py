from awesoon.core import queries
from awesoon.core.db_client import DatabaseApiClient
from dotenv import load_dotenv
load_dotenv()


def get_shop_policies(shop):
    # later we add the type of platform to the shop
    # and we do query[shop.platform] instead of query["shopify"]
    return queries["shopify"].get_shop_policies(shop["shop_url"], shop["access_token"])


def get_shop_products(shop):
    return queries["shopify"].get_shop_products(shop["shop_url"], shop["access_token"])


def get_shop_categories(shop):
    return queries["shopify"].get_shop_categories(shop["shop_url"], shop["access_token"])


def get_shop_orders(shop):
    return queries["shopify"].get_shop_orders(shop["shop_url"], shop["access_token"])
