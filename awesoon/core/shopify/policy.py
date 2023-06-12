import json
import shopify

from awesoon.core.shopify.util import decode_html_policies
api_version = '2023-01'


class ShopifyQuey:

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
         
        

