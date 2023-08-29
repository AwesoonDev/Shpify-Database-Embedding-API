import json
from typing import List

import shopify

from awesoon.core.query import Query
from awesoon.core.resource import Resource
from awesoon.core.shopify.resource import Article, Category, Order, Page, Policy, Product
from awesoon.core.shopify.util import decode_html_policies, get_id_from_gid, strip_tags

API_VERSION = "2023-01"

SHP_FIELDS = [
    "id", "title", "product_type", "body_html", "variants", "handle", "status", "published_at", "tags", "vendor"
]

VARIANT_FIELDS = [
    "id", "title", "grams", "inventory_quantity", "price",
]

ORDER_FIELDS = ["order_status_url", "order_number", "id", "fulfillment_status"]


def process_products_data(product_data):
    products = []
    for product in product_data:
        if product.get("status") == "active" and product.get("published_at"):
            product = {field: product.get(field) for field in SHP_FIELDS}
            product["body_html"] = strip_tags(product.get("body_html"))
            variants = product.get("variants")
            if variants:
                product["variants"] = [{key: variant.get(key) for key in VARIANT_FIELDS} for variant in variants]
            products.append(product)
        else:
            pass
    return products


def process_pages_data(page_data):
    pages = []
    for page in page_data:
        if page.get("published_at"):
            page["body_html"] = strip_tags(page.get("body_html"))
            pages.append(page)
        else:
            pass
    return pages


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
        yield _serialize_docs(policies_decoded, Policy)

    @classmethod
    def get_shop_products(cls, shop_url, token) -> List[Product]:
        data = []
        with shopify.Session.temp(shop_url, API_VERSION, token):
            product_pages = shopify.Product.find()
            while True:
                curr_page_data = [product_page.to_dict() for product_page in product_pages]
                products = process_products_data(curr_page_data)
                yield _serialize_docs(products, Product)
                data.extend(curr_page_data)
                if not product_pages.has_next_page():
                    break
                product_pages = product_pages.next_page()

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
        yield _serialize_docs(categories, Category)

    @classmethod
    def get_shop_orders(cls, shop_url, token) -> List[Order]:
        data = []
        with shopify.Session.temp(shop_url, API_VERSION, token):
            orders = shopify.Order.find()
            while True:
                orders_data = [order.to_dict() for order in orders]
                orders_data = [{field: order.get(field) for field in ORDER_FIELDS} for order in orders_data]
                data.extend(orders_data)
                if not orders.has_next_page():
                    break
                orders = orders.next_page()
        yield _serialize_docs(data, Order)

    @classmethod
    def get_shop_pages(cls, shop_url, token) -> List[Page]:
        data = []
        with shopify.Session.temp(shop_url, API_VERSION, token):
            page_pages = shopify.Page.find()
            while True:
                pages_data = [page.to_dict() for page in page_pages]
                data.extend(process_pages_data(pages_data))
                if not page_pages.has_next_page():
                    break
                page_pages = page_pages.next_page()
        yield _serialize_docs(data, Page)

    @classmethod
    def get_shop_articles(cls, shop_url, token) -> List[Page]:
        data = []
        with shopify.Session.temp(shop_url, API_VERSION, token):
            blog_pages = shopify.Blog.find()
            while True:
                for blog in blog_pages:
                    articles = blog.articles()
                    data.extend([article.to_dict() for article in articles])
                if not blog_pages.has_next_page():
                    break
                blog_pages = blog_pages.next_page()
        yield _serialize_docs(data, Article)
