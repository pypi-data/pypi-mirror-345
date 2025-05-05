class InvalidClickHouseConfigurationError(Exception):
    pass


class ClickHouseConfigurationBuilder:
    def __init__(self, config):
        self._config = config

    def build(self, data):
        self._config._clickhouse_host = data.get('clickhouse_host')
        self._config._clickhouse_port = data.get('clickhouse_port')
        self._config._clickhouse_username = data.get('clickhouse_username')
        self._config._clickhouse_password = data.get('clickhouse_password')
