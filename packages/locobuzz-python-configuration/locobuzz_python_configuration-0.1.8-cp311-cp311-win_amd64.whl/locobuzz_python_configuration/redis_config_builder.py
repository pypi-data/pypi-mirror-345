class InvalidRedisConfigurationError(Exception):
    pass


class RedisConfigurationBuilder:
    def __init__(self, config):
        self._config = config

    def build(self, data):
        self._config._redis_host = data.get('redis_host')
