from flask import request
from awesoon.core.shop import shop_compute
from flask_restx import Namespace, Resource, marshal

from awesoon.api.model.shops import prompt_model
from awesoon.core.exceptions import ShopNotFoundError
import json

ns = Namespace(
    "shops", "This namespace is resposible for shop related data generation")


compute_parser = ns.parser()
compute_parser.add_argument("app", type=str, default=None, location="values")


@ns.route("/<id>/compute")
class ShopCompute(Resource):
    @ns.expect(compute_parser)
    def post(self, id):
        args = compute_parser.parse_args()
        data = shop_compute(id, args)
        return data

