from .config.env_parameters import *
from .config.logging_config import setup_logging, get_logger

setup_logging()
logger = get_logger('init')
logger.debug('Logging initialized in __init__.py')
