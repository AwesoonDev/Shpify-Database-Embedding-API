from flask import request
from awesoon.core.shop import generate_shop_prompt_by_policies, get_shop_policies, get_shop_categories, get_shop_products
from flask_restx import Namespace, Resource, marshal

from awesoon.api.model.shops import prompt_model
from awesoon.core.exceptions import ShopNotFoundError
import json

ns = Namespace(
    "shops", "This namespace is resposible for shop related data generation")

prompt_model = ns.model(
    "model",
    prompt_model
)


@ns.route("/<id>/prompt-generate")
class ShopPromptGenerate(Resource):
    def post(self, id):
        policies = get_shop_policies(id)
        prompt = generate_shop_prompt_by_policies(policies)
        result = {
            "prompt": prompt
        }
        return marshal(result, prompt_model)

@ns.route("/<id>/get-policies")
class ShopGetPolicies(Resource):
    def post(self, id):
        policies = get_shop_policies(id)
        result = {
            "policies": policies
        }
        return result
    
@ns.route("/<id>/get-products")
class ShopGetProducts(Resource):
    def post(self, id):
        products = get_shop_products(id)
        result = {
            "products": products
        }
        return result
    
@ns.route("/<id>/get-categories")
class ShopGetCategories(Resource):
    def post(self, id):
        categories = get_shop_categories(id)
        result = {
            "categories": categories
        }
        return result

# @ns.route("/<id>/compute")
# class ShopCompute(Resource):
#     def post(self, id):

#         return(200)
