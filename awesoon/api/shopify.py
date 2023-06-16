
from awesoon.core.shop import get_shop_categories, get_shop_policies, get_shop_products, shop_compute
from flask_restx import Namespace, Resource

from awesoon.api.model.shops import prompt_model

ns = Namespace(
    "shopify-query", "This namespace is resposible for shop related data generation")

prompt_model = ns.model(
    "model",
    prompt_model
)


@ns.route("/<id>/policies")
class ShopGetPolicies(Resource):
    def get(self, id):
        policies = get_shop_policies(id)
        result = {
            "policies": policies
        }
        return result


@ns.route("/<id>/products")
class ShopGetProducts(Resource):
    def get(self, id):
        products = get_shop_products(id)
        result = {
            "products": products
        }
        return result


@ns.route("/<id>/categories")
class ShopGetCategories(Resource):
    def get(self, id):
        categories = get_shop_categories(id)
        result = {
            "categories": categories
        }
        return result

