from flask import request
from awesoon.core.shop import generate_shop_prompt_by_policies, get_shop_policies
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
