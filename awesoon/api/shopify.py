
from flask_restx import Namespace, Resource

from awesoon.api.utils import add_pagination_params
from awesoon.adapter.db_api_client import DatabaseApiClient
from awesoon.core.shop import (
    get_shop_categories,
    get_shop_orders,
    get_shop_policies,
    get_shop_products,
)

ns = Namespace(
    "shopify-query", "This namespace is resposible for shop related data generation"
)


shopify_parser = ns.parser()
shopify_parser.add_argument("app_name", type=str, default=None, location="values")
shopify_parser = add_pagination_params(shopify_parser)


def paginate_resources(resources, args):
    limit = args["limit"]
    offset = args["offset"]
    return resources[offset:limit]



@ns.route("/<id>/policies")
class ShopGetPolicies(Resource):
    @ns.expect(shopify_parser)
    def get(self, id):
        args = shopify_parser.parse_args()
        shop = DatabaseApiClient.get_shop_installation(id, app_name=args["app_name"])
        policies = get_shop_policies(shop)
        policies = paginate_resources(policies, args)
        result = {
            "policies": [policy.raw() for policy in policies]
        }
        return result


@ns.route("/<id>/products")
class ShopGetProducts(Resource):
    @ns.expect(shopify_parser)
    def get(self, id):
        args = shopify_parser.parse_args()
        shop = DatabaseApiClient.get_shop_installation(id, app_name=args["app_name"])
        products = get_shop_products(shop)
        products = paginate_resources(products, args)
        result = {
            "products": [product.raw() for product in products]
        }
        return result


@ns.route("/<id>/categories")
class ShopGetCategories(Resource):
    @ns.expect(shopify_parser)
    def get(self, id):
        args = shopify_parser.parse_args()
        shop = DatabaseApiClient.get_shop_installation(id, app_name=args["app_name"])
        categories = get_shop_categories(shop)
        categories = paginate_resources(categories, args)
        result = {
            "categories": [category.raw() for category in categories]
        }
        return result


@ns.route("/<id>/orders")
class ShopOrders(Resource):
    @ns.expect(shopify_parser)
    def get(self, id):
        args = shopify_parser.parse_args()
        shop = DatabaseApiClient.get_shop_installation(id, app_name=args["app_name"])
        orders = get_shop_orders(shop)
        orders = paginate_resources(orders, args)
        result = {
            "orders": [order.raw() for order in orders]
        }
        return result
