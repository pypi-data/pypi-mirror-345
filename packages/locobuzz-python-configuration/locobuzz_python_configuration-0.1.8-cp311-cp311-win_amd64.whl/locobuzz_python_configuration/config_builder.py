import json

from jsonschema import validate, ValidationError, SchemaError

from locobuzz_python_configuration.utils_functions import add_extra_properties_to_schema

properties = {
    "sql": ["sql_user_name", "sql_server_ip", "sql_pass_word"],
    "clickhouse": ["clickhouse_host", "clickhouse_port"],
    "aws": ["aws_access_key", "aws_secret_key"],
    "elastic": ["elastic_host", "elastic_username", "elastic_password"],
    "redis": ["redis_host"],
    "kafka": ["broker", "read_topic", "push_topic"]
}


class InvalidConfigurationError(Exception):
    pass


class Configuration:
    def __init__(self, config_file_path=None):
        self._config_file_path = config_file_path
        self._environ = None
        self._log_enabled = None
        self._log_level = None
        self._is_async_logger = None
        self._extra_properties = {}

    def set_common_config(self, data, required_components):
        self._environ = data.get('environ')
        self._log_enabled = data.get('log_enabled')
        self._log_level = data.get('log_level')
        self._is_async_logger = data.get('is_async_logger')
        common_list = ['environ', 'log_enabled', 'log_level', 'is_async_logger']
        for comp in required_components:
            if comp in properties:
                common_list += properties[comp]
        self._extra_properties = {k: v for k, v in data.items() if k not in common_list}

    def get_extra_properties(self):
        return self._extra_properties


class ConfigurationBuilder:
    def __init__(self):
        self._redis_builder = None
        self._configuration = Configuration()
        self._sql_builder = None
        self._clickhouse_builder = None
        self._aws_builder = None
        self._elastic_builder = None
        self._kafka_builder = None
        self.required_components = []
        self._app_settings_path = None

    def load_from_file(self, file_path, required_components=[]):
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
                self._app_settings_path = file_path
                self.required_components = required_components
                self.validate_json(data)
                self.set_configuration(data, self.required_components)
        except FileNotFoundError:
            raise InvalidConfigurationError(f"Configuration file '{file_path}' not found.")
        except json.JSONDecodeError:
            raise InvalidConfigurationError("Invalid JSON format.")
        except ValidationError as ve:
            raise InvalidConfigurationError(f"JSON validation error: {ve.message}")
        except SchemaError as se:
            raise InvalidConfigurationError(f"JSON schema error: {se.message}")

    def load_from_dict(self, data, required_components=[]):
        try:
            self.required_components = required_components
            self.validate_json(data)
            self.set_configuration(data, required_components)
        except ValidationError as ve:
            raise InvalidConfigurationError(f"JSON validation error: {ve.message}")
        except SchemaError as se:
            raise InvalidConfigurationError(f"JSON schema error: {se.message}")

    def validate_json(self, data):
        schema = {
            "type": "object",
            "properties": {
                "environ": {"type": "string"},
                "sql_user_name": {"type": "string"},
                "sql_server_ip": {"type": "string"},
                "sql_pass_word": {"type": "string"},
                "clickhouse_host": {"type": "string"},
                "clickhouse_port": {"type": "string"},
                "clickhouse_username": {"type": "string"},
                "clickhouse_password": {"type": "string"},
                "elastic_host": {"type": "string"},
                "elastic_username": {"type": "string"},
                "elastic_password": {"type": "string"},
                "elastic_mention_index_name": {"type": "string"},
                "elastic_author_index_name": {"type": "string"},
                "opensearch_python_service_endpoint": {"type": "string"},
                "aws_access_key": {"type": "string"},
                "aws_secret_key": {"type": "string"},
                "s3_bucket_name": {"type": "string"},
                "aws_s3_base_url": {"type": "string"},
                "service_ng_api": {"type": "string"},
                "broker": {"type": "string"},
                "read_topic": {"type": "string"},
                "dead_letter_topic_name": {"type": "string"},
                "g_chat_hook": {"type": "string"},
                "g_chat_error_hook": {"type": "string"},
                "log_enabled": {"type": "string"},
                "redis_host": {"type": "string"}
            },
            "required": ["environ", "log_enabled", "is_async_logger", "log_level"]
        }
        updated_schema = add_extra_properties_to_schema(schema, self._app_settings_path)
        validate(instance=data, schema=updated_schema)
        self.validate_required_components(data)

    def validate_required_components(self, data):
        if "sql" in self.required_components:
            if not data.get('sql_user_name') or not data.get('sql_server_ip') or not data.get('sql_pass_word'):
                raise InvalidConfigurationError("Missing SQL configuration properties")

        if "clickhouse" in self.required_components:
            if not data.get('clickhouse_host') or not data.get('clickhouse_port'):
                raise InvalidConfigurationError("Missing ClickHouse configuration properties")

        if "aws" in self.required_components:
            if not data.get('aws_access_key') or not data.get('aws_secret_key'):
                raise InvalidConfigurationError("Missing AWS configuration properties")

        if "elastic" in self.required_components:
            if not data.get('elastic_host') or not data.get('elastic_username') or not data.get('elastic_password'):
                raise InvalidConfigurationError("Missing ElasticSearch configuration properties")

        if "kafka" in self.required_components:
            if not data.get('broker'):
                if not data.get('read_topic') or not data.get("push_topic"):
                    raise InvalidConfigurationError("Missing Kafka configuration properties")

        if "redis" in self.required_components:
            if not data.get('redis_host'):
                raise InvalidConfigurationError("Missing Redis configuration properties")

    def set_configuration(self, data, required_components=[]):
        self._configuration.set_common_config(data, required_components)

        if self._sql_builder:
            self._sql_builder.build(data)
        if self._clickhouse_builder:
            self._clickhouse_builder.build(data)
        if self._aws_builder:
            self._aws_builder.build(data)
        if self._elastic_builder:
            self._elastic_builder.build(data)
        if self._kafka_builder:
            self._kafka_builder.build(data)
        if self._redis_builder:
            self._redis_builder.build(data)

    def set_sql_builder(self, builder):
        self._sql_builder = builder

    def set_clickhouse_builder(self, builder):
        self._clickhouse_builder = builder

    def set_aws_builder(self, builder):
        self._aws_builder = builder

    def set_elastic_builder(self, builder):
        self._elastic_builder = builder

    def set_kafka_builder(self, builder):
        self._kafka_builder = builder

    def set_redis_builder(self, builder):
        self._redis_builder = builder

    def get_configuration(self):
        return self._configuration
