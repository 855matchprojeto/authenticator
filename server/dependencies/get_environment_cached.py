from server.configuration.environment import Environment
from functools import lru_cache


@lru_cache
def get_environment_cached():
    return Environment()

