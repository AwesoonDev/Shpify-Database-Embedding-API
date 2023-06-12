import logging
import os
from pathlib import Path

from config_probe import probe

RESOURCES_PATH = Path(__file__).parent.parent / 'deploy' / 'config'
env = os.environ.get("ENVIRONMENT", "local")


def load(environment):
    config_file = 'common.yaml'
    env_config_file = '{}/config.yaml'.format(environment)
    logging.info('Loading config {} and {}'.format(
        config_file,
        env_config_file
    ))

    config = probe(path=str(RESOURCES_PATH), patterns=[config_file, env_config_file])
    config.database.url = f"{config.database.host}:{config.database.port}/{config.database.api_version}"
    config.database.url_api_version = f"{config.database.host}:{config.database.port}/{config.database.api_version}"

    return config


config = load(env)
