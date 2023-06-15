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
        fields = ['id', 'title', 'product_type', 'body_html', 'variants', 'options', 'published_at', 'handle', 'status', 'tags', 'vendor']
        variants_fields = ['compare_at_price', 'fulfillment_service', 'grams', 'inventory_policy', 'inventoryLevel', 'inventory_quantity', 'option', 'price', 'taxable']
        with shopify.Session.temp(shop_url, api_version, token):
            product_pages = shopify.Product.find(fields = fields)
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
                product['variants'] = [{key: variant.pop(key, None) for key in variants_fields} for variant in variants]

            options = product.pop('options', None)
            if options:
                product['options'] = [option.__dict__['attributes'] for option in options]

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
        categories = [node.pop('productTaxonomyNode').pop('fullName', None) for node in categories_trimmed ]
        return categories

