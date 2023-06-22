import json
from typing import List
import requests
import shopify
from awesoon.core.query import Query
from awesoon.core.shopify.documents import Category, Policy, Product, ShopifyObject

from awesoon.core.shopify.util import decode_html_policies, strip_tags
API_VERSION = "2023-01"

SHP_FIELDS = [
    "id", "title", "product_type", "body_html", "variants", "handle", "status", "tags", "vendor"
    # "options", "published_at",  
]

VARIANT_FIELDS = [
    "id", "title", "grams", "inventory_quantity", "price",
    # "compare_at_price", "fulfillment_service",  "inventory_policy",
    # "inventoryLevel",  "option",  "taxable"
]


def _make_gql_request(shop_url, token, query):
    data = None
    with shopify.Session.temp(shop_url, API_VERSION, token):
        data = shopify.GraphQL().execute(query)
    return json.loads(data)


def _serialize_docs(raw_docs, type):
    return [type(doc) for doc in raw_docs]


class ShopifyQuery(Query):
    @classmethod
    def get_shop_policies(cls, shop_url, token) -> List[Policy]:
        query = """
        {
            shop {
                shopPolicies {
                    body
                }
            }
        }"""
        policies_object = _make_gql_request(shop_url, token, query)
        policies_trimmed = policies_object["data"].get("shop", {}).get("shopPolicies")
        policies_decoded = decode_html_policies(policies_trimmed)
        return _serialize_docs(policies_decoded, Policy)

    @classmethod
    def get_shop_products(cls, shop_url, token) -> List[Product]:
        data = []
        with shopify.Session.temp(shop_url, API_VERSION, token):
            product_pages = shopify.Product.find()
            while True:
                curr_page_data = [product_page.to_dict() for product_page in product_pages]
                data.extend(curr_page_data)
                if not product_pages.has_next_page():
                    break
                product_pages = product_pages.next_page()
        products = []
        for product in data:
            if product.get("status", None) == "active":
                product = {field: product.get(field) for field in SHP_FIELDS}
                product["body_html"] = strip_tags(product.pop("body_html", None))
                product["url"] = f"""{shop_url}/products/{product.pop("handle", None)}"""
                variants = product.get("variants")
                if variants:
                    product["variants"] = [{key: variant.get(key) for key in VARIANT_FIELDS} for variant in variants]
                    for variant in product["variants"]:
                        variant["url"] = f"""{product.get("url")}?variant={variant.get("id")}"""
                products.append(product)
            else:
                pass
        return _serialize_docs(products, Product)

    @classmethod
    def get_shop_categories(cls, shop_url, token) -> List[Category]:
        query = """
        {
            shop {
                allProductCategories {
                    productTaxonomyNode {
                        fullName
                        name
                        id
                    }
                }
            }
        }"""

        categories_object = _make_gql_request(shop_url, token, query)
        categories_trimmed = categories_object["data"].get("shop", {}).get("allProductCategories")
        categories = [
            node.pop("productTaxonomyNode").pop("fullName", None) for node in categories_trimmed
        ]
        return _serialize_docs(categories, Category)

    @classmethod
    def get_shop_orders(cls, shop_url, token) -> List[ShopifyObject]:
        data = []
        with shopify.Session.temp(shop_url, API_VERSION, token):
            orders = shopify.Order.find()
            while True:
                orders_data = [order.to_dict() for order in orders]
                data.extend(orders_data)
                if not orders.has_next_page():
                    break
                orders = orders.next_page()
        return _serialize_docs(data, ShopifyObject)
