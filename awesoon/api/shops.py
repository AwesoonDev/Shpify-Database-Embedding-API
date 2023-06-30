from flask_restx import Namespace, Resource, marshal

from awesoon.celery.tasks import manual_scan_request
from awesoon.core.exceptions import ShopInstallationNotFoundError
from awesoon.core.models.scan import Scan, ScanStatus, TriggerType
from awesoon.core.scan import Scanner

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
            scan: Scan = Scanner.create_scan(int(id))
            manual_scan_request.delay(scan.id)
            return scan.id, 202
        except ShopInstallationNotFoundError:
            ns.abort(400, "Shop Installation Not Found")


@ns.route("/<id>/compute-no-celery")
class ShopComputeNonCelery(Resource):
    @ns.expect(compute_parser)
    def post(self, id):
        try:
            args = compute_parser.parse_args()
            scan: Scan = Scanner.create_scan(int(id))
            Scanner.scan(scan)
            return scan.id, 200
        except ShopInstallationNotFoundError:
            ns.abort(400, "Shop Installation Not Found")
