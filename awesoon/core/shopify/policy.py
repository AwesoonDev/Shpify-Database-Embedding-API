import json
import shopify

from awesoon.core.shopify.util import decode_html_policies, strip_tags
api_version = '2023-01'


class ShopifyQuery:
    @classmethod
    def get_shop_policies(cls, shop_url, token):
        data = None
        with shopify.Session.temp(shop_url, api_version, token):
            data = shopify.GraphQL().execute(
                """{
                    shop {
                        shopPolicies {
                            body
                            id
                        }
                    }
                }"""
            )
        
        policies_object = json.loads(data)
        policies_trimmed = policies_object["data"].get("shop", {}).get("shopPolicies")
        policies_decoded = decode_html_policies(policies_trimmed)
        return policies_decoded

    @classmethod
    def get_shop_products(cls, shop_url, token):
        data = []
        with shopify.Session.temp(shop_url, api_version, token):
            product_pages = shopify.Product.find()
            while True:
                curr_page_data = [product_page.__dict__['attributes'] for product_page in product_pages]
                data.extend(curr_page_data)
                if not product_pages.has_next_page():
                    break
                product_pages = product_pages.next_page()

        for product in data:
            product['body_html'] = strip_tags(product['body_html'])
            product['variants'] = [variant.__dict__['attributes'] for variant in product['variants']]
            product['options'] = [option.__dict__['attributes'] for option in product['options']]
            product['images'] = None
            product['image'] = None

        return(data)

    @classmethod
    def get_shop_categories(cls, shop_url, token):
        data = None
        with shopify.Session.temp(shop_url, api_version, token):
            data = shopify.GraphQL().execute(
                """{
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
            )

        categories_object = json.loads(data)
        categories_trimmed = categories_object["data"].get("shop", {}).get("allProductCategories")
        return categories_trimmed

