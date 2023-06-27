import logging
import os

from flask import Blueprint, Flask
from flask_restx import Api
from flask_cors import CORS

from awesoon.api.shops import ns as shops_ns
from awesoon.api.shopify import ns as shopify_ns
from awesoon.api.health import ns as health_ns
from awesoon.config import load

config = load(os.environ.get('ENVIRONMENT', 'local'))
logging.basicConfig(level=logging.DEBUG)


def create_app():
    app = Flask(__name__)
    CORS(app, resource={r"/*": {"origins": "*"}})
    v1_blueprint = Blueprint("shop-api", __name__, url_prefix="/v1")
    api_v1 = Api(v1_blueprint, title="Awesoon Shop API", version="1.0", description="Awesoon SHOP API")
    health_blueprint = Blueprint("awesoon-shop-health", __name__)
    api_health = Api(
        health_blueprint,
        title="Awesoon shop api health",
        description="non-versioned namespaces. SEE /v1 FOR " "THE VERSIONED API",
    )

    api_health.add_namespace(health_ns, path='/health')
    api_v1.add_namespace(shops_ns)
    api_v1.add_namespace(shopify_ns)
    app.register_blueprint(v1_blueprint)
    app.register_blueprint(health_blueprint)

    return app
