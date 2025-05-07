"""Environment parameter management for MCard."""
import os
from dotenv import load_dotenv
from .config_constants import (
    ENV_HASH_ALGORITHM,
    ENV_DB_PATH,
    ENV_DB_MAX_CONNECTIONS,
    ENV_DB_TIMEOUT,
    ENV_SERVICE_LOG_LEVEL,
    ENV_API_PORT,
    ENV_API_KEY,
    ENV_HASH_CUSTOM_MODULE,
    ENV_HASH_CUSTOM_FUNCTION,
    ENV_HASH_CUSTOM_LENGTH,
    DEFAULT_DB_PATH,
    TEST_DB_PATH,
    DEFAULT_POOL_SIZE,
    DEFAULT_TIMEOUT,
    DEFAULT_API_KEY,
    DEFAULT_API_PORT,
)

class EnvParameters:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EnvParameters, cls).__new__(cls)
            cls._instance.load_env_variables()
        return cls._instance

    def load_env_variables(self):
        """Load environment variables with appropriate defaults from config_constants."""
        load_dotenv()
        self.MCARD_DB_PATH = os.getenv(ENV_DB_PATH, DEFAULT_DB_PATH)
        self.TEST_DB_PATH = os.getenv('TEST_DB_PATH', TEST_DB_PATH)
        self.MCARD_SERVICE_LOG_LEVEL = os.getenv(ENV_SERVICE_LOG_LEVEL, 'DEBUG')
        self.DEFAULT_POOL_SIZE = int(os.getenv('DEFAULT_POOL_SIZE', DEFAULT_POOL_SIZE))
        self.DEFAULT_TIMEOUT = float(os.getenv(ENV_DB_TIMEOUT, DEFAULT_TIMEOUT))
        self.MCARD_HASH_ALGORITHM = os.getenv(ENV_HASH_ALGORITHM)  # No default, let HashAlgorithm handle it
        self.MCARD_HASH_CUSTOM_MODULE = os.getenv(ENV_HASH_CUSTOM_MODULE, 'custom_module')
        self.MCARD_HASH_CUSTOM_FUNCTION = os.getenv(ENV_HASH_CUSTOM_FUNCTION, 'custom_function')
        self.MCARD_HASH_CUSTOM_LENGTH = int(os.getenv(ENV_HASH_CUSTOM_LENGTH, 64))
        self.MCARD_API_PORT = int(os.getenv(ENV_API_PORT, DEFAULT_API_PORT))
        self.MCARD_STORE_MAX_CONNECTIONS = int(os.getenv(ENV_DB_MAX_CONNECTIONS, DEFAULT_POOL_SIZE))
        self.MCARD_API_KEY = os.getenv(ENV_API_KEY, DEFAULT_API_KEY)

    def get_db_path(self):
        return self.MCARD_DB_PATH

    def get_test_db_path(self):
        return self.TEST_DB_PATH

    def get_log_level(self):
        return self.MCARD_SERVICE_LOG_LEVEL

    def get_default_pool_size(self):
        return self.DEFAULT_POOL_SIZE

    def get_default_timeout(self):
        return self.DEFAULT_TIMEOUT

    def get_hash_algorithm(self):
        return self.MCARD_HASH_ALGORITHM

    def get_hash_custom_module(self):
        return self.MCARD_HASH_CUSTOM_MODULE

    def get_hash_custom_function(self):
        return self.MCARD_HASH_CUSTOM_FUNCTION

    def get_hash_custom_length(self):
        return self.MCARD_HASH_CUSTOM_LENGTH

    def get_api_port(self):
        return self.MCARD_API_PORT

    def get_store_max_connections(self):
        return self.MCARD_STORE_MAX_CONNECTIONS

    def get_api_key(self):
        return self.MCARD_API_KEY
