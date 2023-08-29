
from flask_restx import Namespace, Resource

from awesoon.api.utils import add_pagination_params
from awesoon.adapter.db.shop_client import DatabaseShopClient
from awesoon.core.shop import (
    get_shop_categories,
    get_shop_orders,
    get_shop_pages,
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
        shop = DatabaseShopClient.get_shop_installation(id, app_name=args["app_name"])
        policies_generator = get_shop_policies(shop)
        policies_data = []
        for policies in policies_generator:
            policies_data.extend(policies)
        policies = paginate_resources(policies_data, args)
        result = {
            "policies": [policy.raw() for policy in policies]
        }
        return result


@ns.route("/<id>/products")
class ShopGetProducts(Resource):
    @ns.expect(shopify_parser)
    def get(self, id):
        args = shopify_parser.parse_args()
        shop = DatabaseShopClient.get_shop_installation(id, app_name=args["app_name"])
        products_generator = get_shop_products(shop)
        products_data = []
        for products in products_generator:
            products_data.extend(products)
        products = paginate_resources(products_data, args)
        result = {
            "products": [product.raw() for product in products]
        }
        return result


@ns.route("/<id>/categories")
class ShopGetCategories(Resource):
    @ns.expect(shopify_parser)
    def get(self, id):
        args = shopify_parser.parse_args()
        shop = DatabaseShopClient.get_shop_installation(id, app_name=args["app_name"])
        categories_generator = get_shop_categories(shop)
        categories_data = []
        for categories in categories_generator:
            categories_data.extend(categories)
        categories = paginate_resources(categories_data, args)
        result = {
            "categories": [category.raw() for category in categories]
        }
        return result


@ns.route("/<id>/pages")
class ShopPages(Resource):
    @ns.expect(shopify_parser)
    def get(self, id):
        args = shopify_parser.parse_args()
        shop = DatabaseShopClient.get_shop_installation(id, app_name=args["app_name"])
        pages_generator = get_shop_pages(shop)
        pages_data = []
        for pages in pages_generator:
            pages_data.extend(pages)
        pages = paginate_resources(pages_data, args)
        result = {
            "pages": [page.raw() for page in pages]
        }
        return result


@ns.route("/<id>/orders")
class ShopOrders(Resource):
    @ns.expect(shopify_parser)
    def get(self, id):
        args = shopify_parser.parse_args()
        shop = DatabaseShopClient.get_shop_installation(id, app_name=args["app_name"])
        orders_generator = get_shop_orders(shop)
        order_data = []
        for order in orders_generator:
            order_data.extend(order)
        orders = paginate_resources(order_data, args)
        result = {
            "orders": [order.raw() for order in orders]
        }
        return result

