import json
import shopify

from awesoon.core.shopify.util import decode_html_policies
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
        
        data = json.loads(data)
        policies = data["data"].get("shop", {}).get("shopPolicies")
        return decode_html_policies(policies)
    
    # get vendors

    @classmethod
    def get_shop_products(cls, shop_url, token):
        data = None
        with shopify.Session.temp(shop_url, api_version, token):
            data = shopify.Product.find()

        data = json.loads(data)
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
         
        

