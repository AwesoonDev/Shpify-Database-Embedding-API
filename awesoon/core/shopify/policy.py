import json
import shopify

from awesoon.core.shopify.util import decode_html_policies
api_version = '2023-01'


class ShopifyQuery:

# This method collects all data that is to be vectorized and stored as raw text in the
# store specific database by db-api. it returns a json-able object to be transmitted directly
# to a db-api endpoint.
    @classmethod
    def shop_compute(als, shop_url, token):
        data = None
        with shopify.Session.temp(shop_url, api_version, token):
            policies = shopify.GraphQL().execute(
                """{
                    shop {
                        shopPolicies {
                            body
                            id
                        }
                    }
                }"""
            )

            pols1 = json.loads(policies)
            pols2 = pols1["data"].get("shop", {}).get("shopPolicies")
            pols = decode_html_policies(pols2)

            prods = []
            product_pages = shopify.Product.find()
            while True:
                curr_page_data = [product_page.__dict__['attributes'] for product_page in product_pages]
                prods.extend(curr_page_data)
                if not product_pages.has_next_page():
                    break
                product_pages = product_pages.next_page()

            for product in prods:
                product['variants'] = [variant.__dict__['attributes'] for variant in product['variants']]
                product['options'] = [option.__dict__['attributes'] for option in product['options']]
                product['images'] = None
                product['image'] = None

            categories = shopify.GraphQL().execute(
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

            cats1 = json.loads(categories)
            cats2 = cats1["data"].get("shop", {}).get("allProductCategories")
            cats = cats2

            print(type(pols), type(prods), type(cats))

            data = {
                "policies": pols,
                "products": prods,
                "categories": cats
            }

            return data






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
        
        data = json.loads(data)
        policies = data["data"].get("shop", {}).get("shopPolicies")
        return decode_html_policies(policies)
    
    # get vendors

    @classmethod
    def get_shop_products(cls, shop_url, token):
        products = None
        data = []
        with shopify.Session.temp(shop_url, api_version, token):
            products = shopify.Product.find()
            while True:
                curr_page_data = [product.__dict__['attributes'] for product in products]
                data.extend(curr_page_data)
                if not products.has_next_page():
                    break
                products = products.next_page()

        for product in data:
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

        data = json.loads(data)
        return(data)
         
        

