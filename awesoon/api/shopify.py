
from awesoon.core.shop import get_shop_categories, get_shop_policies, get_shop_products, shop_compute
from flask_restx import Namespace, Resource


ns = Namespace(
    "shopify-query", "This namespace is resposible for shop related data generation")


shopify_parser = ns.parser()
shopify_parser.add_argument("app", type=str, default=None, location="values")


@ns.route("/<id>/policies")
class ShopGetPolicies(Resource):
    @ns.expect(shopify_parser)
    def get(self, id):
        args = shopify_parser.parse_args()
        policies = get_shop_policies(id, args["app"])
        result = {
            "policies": policies
        }
        return result


@ns.route("/<id>/products")
class ShopGetProducts(Resource):
    @ns.expect(shopify_parser)
    def get(self, id):
        args = shopify_parser.parse_args()
        products = get_shop_products(id, args["app"])
        result = {
            "products": products
        }
        return result


@ns.route("/<id>/categories")
class ShopGetCategories(Resource):
    @ns.expect(shopify_parser)
    def get(self, id):
        args = shopify_parser.parse_args()
        categories = get_shop_categories(id, args["app"])
        result = {
            "categories": categories
        }
        return result
