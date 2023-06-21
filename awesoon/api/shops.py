from flask import request
from awesoon.core.exceptions import ShopInstallationNotFoundError
from awesoon.core.docs import shop_compute
from flask_restx import Namespace, Resource, marshal


ns = Namespace(
    "shops", "This namespace is resposible for shop related data generation")


compute_parser = ns.parser()
compute_parser.add_argument("app_name", type=str, default=None, location="values")


@ns.route("/<id>/compute")
class ShopCompute(Resource):
    @ns.expect(compute_parser)
    def post(self, id):
        try:
            args = compute_parser.parse_args()
            status = shop_compute(id, args)
            if status:
                return {"message": "success"}, 200
            ns.abort(400, "Could not compute")
        except ShopInstallationNotFoundError:
            ns.abort(400, "Shop Installation Not Found")
