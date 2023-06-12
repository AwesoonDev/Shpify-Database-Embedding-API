"""health.py

An indicator to check whether this service is up or down.
"""
import logging

from flask_restx import Namespace, Resource, fields

STATUS_DOWN = "DOWN"
STATUS_UP = "UP"

logger = logging.getLogger(__name__)

ns = Namespace("health", "Health check related endpoints")

simple_status_report = ns.model(
    "simple_status_report",
    {
        "status": fields.String(
            description="Current status of this geo (UP or DOWN)"
        ),
    },
)


@ns.route("")
class HealthCheck(Resource):
    @ns.marshal_with(simple_status_report)
    @ns.doc(
        responses={
            200: "Up and running",
            500: "Health check failed",
        }
    )
    def get(self):
        """Returns status of this app."""
        return {"status": STATUS_UP}
