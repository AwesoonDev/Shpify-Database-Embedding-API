from abc import ABC

from awesoon.config import config


class DatabaseClient(ABC):
    config = config
    db_base_url = config.database.url_api_version

    @classmethod
    def _gen_url(cls, route):
        return f"{cls.db_base_url}/{route}"

    @classmethod
    def _make_request(cls, method, route, **kwargs):
        response = method(cls._gen_url(route), **kwargs)
        response.raise_for_status()
        return response.json()
