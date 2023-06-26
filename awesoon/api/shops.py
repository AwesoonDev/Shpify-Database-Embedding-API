from flask import request
from awesoon.core.exceptions import ShopInstallationNotFoundError
from awesoon.core.docs import scan_shop, initiate_scan
from awesoon.core.models.scan import Scan, ScanStatus, TriggerType
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
            new_scan = Scan(
                status=ScanStatus.PENDING.value,
                trigger_type=TriggerType.MANUAL.value,
                shop_id=id
            )
            scan_id, status = initiate_scan(new_scan)
            status = scan_shop(id, scan_id, args)
            if status:
                return {"message": "success"}, 200
            ns.abort(400, "Could not compute")
        except ShopInstallationNotFoundError:
            ns.abort(400, "Shop Installation Not Found")
