import json
from typing import List
import requests
import shopify
from awesoon.core.query import Query
from awesoon.core.shopify.documents import Category, Policy, ShopifyResource

from awesoon.core.shopify.util import decode_html_policies, strip_tags, get_id_from_gid, split_product
API_VERSION = "2023-01"


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
                    id
                    type
                    body
                    url
                }
            }
        }"""
        policies_object = _make_gql_request(shop_url, token, query)
        policies_trimmed = policies_object["data"].get("shop", {}).get("shopPolicies")
        policies_decoded = decode_html_policies(policies_trimmed)
        for policy in policies_decoded:
            policy["id"] = get_id_from_gid(policy.get("id"))
        return _serialize_docs(policies_decoded, Policy)

    @classmethod
    def get_shop_products(cls, shop_url, token) -> List[ShopifyResource]:
        data = []
        with shopify.Session.temp(shop_url, API_VERSION, token):
            product_pages = shopify.Product.find()
            while True:
                curr_page_data = [product_page.to_dict() for product_page in product_pages]
                data.extend(curr_page_data)
                if not product_pages.has_next_page():
                    break
                product_pages = product_pages.next_page()
        ProductDetails, ProductBodies, ProductVariants = [], [], []
        for product in data:
            if product.get("status") == "active" and product.get("published_at"):
                detail, body, variants = split_product(product, shop_url)
                ProductDetails.append(detail)
                ProductBodies.append(body)
                ProductVariants.extend(variants)
            else:
                pass
        Resources = []
        Resources.extend(ProductDetails)
        Resources.extend(ProductBodies)
        Resources.extend(ProductVariants)
        
        return Resources

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
        trimmed_categories = categories_object["data"].get("shop", {}).get("allProductCategories")
        categories = [node.pop("productTaxonomyNode") for node in trimmed_categories]
        for category in categories:
            category["id"] = get_id_from_gid(category.get("id"))
        return _serialize_docs(categories, Category)

    @classmethod
    def get_shop_orders(cls, shop_url, token) -> List[ShopifyResource]:
        data = []
        with shopify.Session.temp(shop_url, API_VERSION, token):
            orders = shopify.Order.find()
            while True:
                orders_data = [order.to_dict() for order in orders]
                data.extend(orders_data)
                if not orders.has_next_page():
                    break
                orders = orders.next_page()
        return _serialize_docs(data, ShopifyResource)
