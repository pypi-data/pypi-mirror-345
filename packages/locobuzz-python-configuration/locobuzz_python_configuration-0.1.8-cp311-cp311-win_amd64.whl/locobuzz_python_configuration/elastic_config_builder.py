class InvalidElasticConfigurationError(Exception):
    pass


class ElasticSearchConfigurationBuilder:
    def __init__(self, config):
        self._config = config

    def build(self, data):
        self._config._elastic_host = data.get('elastic_host')
        self._config._elastic_username = data.get('elastic_username')
        self._config._elastic_password = data.get('elastic_password')
        self._config._elastic_mention_index_name = data.get('elastic_mention_index_name')
        self._config._elastic_author_index_name = data.get('elastic_author_index_name')
        self._config._opensearch_python_service_endpoint = data.get('opensearch_python_service_endpoint')
