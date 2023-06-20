from awesoon.core.db_client import DatabaseApiClient
from awesoon.core.shopify.query import ShopifyQuery
from dotenv import load_dotenv
load_dotenv()

db = DatabaseApiClient()


def get_shop_policies(shop_id, app_name):
    shop = db.get_shop_installation(shop_id, app_name=app_name)
    return ShopifyQuery.get_shop_policies(shop["shop_url"], shop["access_token"])


def get_shop_products(shop_id, app_name):
    shop = db.get_shop_installation(shop_id, app_name=app_name)
    return ShopifyQuery.get_shop_products(shop["shop_url"], shop["access_token"])


def get_shop_categories(shop_id, app_name):
    shop = db.get_shop_installation(shop_id, app_name=app_name)
    return ShopifyQuery.get_shop_categories(shop["shop_url"], shop["access_token"])


def get_shop_orders(shop_id, app_name):
    shop = db.get_shop_installation(shop_id, app_name=app_name)
    return ShopifyQuery.get_shop_orders(shop["shop_url"], shop["access_token"])

