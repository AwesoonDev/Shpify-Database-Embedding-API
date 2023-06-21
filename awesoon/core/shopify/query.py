import json
import requests
import shopify
from awesoon.core.query import Query

from awesoon.core.shopify.util import decode_html_policies, strip_tags
API_VERSION = '2023-01'

SHP_FIELDS = [
    'id', 'title', 'product_type', 'body_html', 'variants',
    'options', 'published_at', 'handle', 'status', 'tags', 'vendor'
]

VARIANT_FIELDS = [
    'compare_at_price', 'fulfillment_service', 'grams', 'inventory_policy',
    'inventoryLevel', 'inventory_quantity', 'option', 'price', 'taxable'
]


def _make_gql_request(shop_url, token, query):
    data = None
    with shopify.Session.temp(shop_url, API_VERSION, token):
        data = shopify.GraphQL().execute(query)
    return json.loads(data)


class ShopifyQuery(Query):
    @classmethod
    def get_shop_policies(cls, shop_url, token):
        query = """
        {
            shop {
                shopPolicies {
                    body
                    id
                }
            }
        }"""
        policies_object = _make_gql_request(shop_url, token, query)
        policies_trimmed = policies_object["data"].get("shop", {}).get("shopPolicies")
        policies_decoded = decode_html_policies(policies_trimmed)
        return policies_decoded

    @classmethod
    def get_shop_products(cls, shop_url, token):
        data = []
        with shopify.Session.temp(shop_url, API_VERSION, token):
            product_pages = shopify.Product.find(fields=SHP_FIELDS)
            while True:
                curr_page_data = [product_page.__dict__['attributes'] for product_page in product_pages]
                data.extend(curr_page_data)
                if not product_pages.has_next_page():
                    break
                product_pages = product_pages.next_page()

        for product in data:
            product['body_html'] = strip_tags(product.pop('body_html', None))
            # product['url'] = ".myshopify.com/" + product.pop('handle', None)
            variants = product.pop('variants', None)
            if variants:
                variants = [variant.__dict__['attributes'] for variant in variants]
                product['variants'] = [{key: variant.pop(key, None) for key in VARIANT_FIELDS} for variant in variants]

            options = product.pop('options', None)
            if options:
                product['options'] = [option.__dict__['attributes'] for option in options]

        return data

    @classmethod
    def get_shop_categories(cls, shop_url, token):
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
            node.pop('productTaxonomyNode').pop('fullName', None) for node in categories_trimmed
        ]
        return categories

    @classmethod
    def get_shop_orders(cls, shop_url, token):
        data = []
        with shopify.Session.temp(shop_url, API_VERSION, token):
            orders = shopify.Order.find()
            while True:
                orders_data = [order.to_dict() for order in orders]
                data.extend(orders_data)
                if not orders.has_next_page():
                    break
                orders = orders.next_page()
        return data
