# config_package/__init__.py

from locobuzz_python_configuration.config_builder import ConfigurationBuilder
from locobuzz_python_configuration.logger_config import setup_logger
from locobuzz_python_configuration.redis_config_builder import RedisConfigurationBuilder
from locobuzz_python_configuration.sql_config_builder import SQLConfigurationBuilder
from locobuzz_python_configuration.clickhouse_config_builder import ClickHouseConfigurationBuilder
from locobuzz_python_configuration.aws_config_builder import AWSConfigurationBuilder
from locobuzz_python_configuration.elastic_config_builder import ElasticSearchConfigurationBuilder
from locobuzz_python_configuration.kafka_config_builder import KafkaConfigurationBuilder


def create_configuration(file_path=None, config_data=None, required_components=[],
                         builder_classes=None):
    builder = ConfigurationBuilder()

    default_builders = {
        'sql': SQLConfigurationBuilder,
        'clickhouse': ClickHouseConfigurationBuilder,
        'aws': AWSConfigurationBuilder,
        'elastic': ElasticSearchConfigurationBuilder,
        'kafka': KafkaConfigurationBuilder,
        'redis': RedisConfigurationBuilder
    }

    # Merge default builders with provided builders, if any
    if builder_classes:
        default_builders.update(builder_classes)

    # Setting the specific builders
    if 'sql' in default_builders:
        builder.set_sql_builder(default_builders['sql'](builder.get_configuration()))
    if 'clickhouse' in default_builders:
        builder.set_clickhouse_builder(default_builders['clickhouse'](builder.get_configuration()))
    if 'aws' in default_builders:
        builder.set_aws_builder(default_builders['aws'](builder.get_configuration()))
    if 'elastic' in default_builders:
        builder.set_elastic_builder(default_builders['elastic'](builder.get_configuration()))
    if 'kafka' in default_builders:
        builder.set_kafka_builder(default_builders['kafka'](builder.get_configuration()))
    if 'redis' in default_builders:
        builder.set_redis_builder(default_builders['redis'](builder.get_configuration()))

    try:
        if file_path:
            builder.load_from_file(file_path, required_components)
        elif config_data:
            builder.load_from_dict(config_data, required_components)
        else:
            raise ValueError("Either file_path or config_data must be provided")

        return builder.get_configuration()
    except Exception as e:
        print(f"Error creating configuration: {e}")
        raise e


# if __name__ == "__main__":
    #     CONFIG = create_configuration(file_path='appsettings.json', required_components=["redis", "kafka"])
    #     print(CONFIG.__dict__)
    #     SERVICE_NAME = "FACEBOOK_PAGE_INSIGHT_READER_SERVICE"
    #     IS_ASYNC_LOGGER = CONFIG.__dict__.get('_is_async_logger', False)
    #     LOG_LEVEL = CONFIG.__dict__.get('_log_level', 'INFO')

    # def configure_logger(service_name, config):
    #     is_async_logger = False
    #     log_level = 'INFO'
    #     log_type = ''
    #     logger = setup_logger(service_name, async_mode=is_async_logger, log_level_str=log_level)
    #     logger.info("Logger configured" + (" in async mode" if is_async_logger else ""))
    #     log_enabled = "PRODUCTION"
    #     logger.info(f"Log enabled for environment: {log_enabled}")
    #     return logger, log_enabled
    #
    #
    # def print_log(config):
    #     logger, log_enabled = configure_logger("service", config)
    #     logger.info("This is an info message")
    #     logger.debug("This is a debug message")
    #     logger.warning("This is a warning message")
    #     logger.error("This is an error message")
    #
    #
    # def configure():
    #     configuration = create_configuration(file_path='appsettings.json', required_components=["sql"]).__dict__
    #     print_log(configuration)
    #
    #
    # configure()
