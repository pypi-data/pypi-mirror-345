import asyncio
import json
import logging
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from logging import Logger
from typing import Union, Callable

from pytz import timezone


def time_tz(*args) -> datetime.timetuple:
    """Get the current time in the Asia/Kolkata timezone."""
    return datetime.now(timezone('Asia/Kolkata')).timetuple()


logging.Formatter.converter = time_tz


class CustomLogger(logging.Logger):
    def error(self, msg, *args, **kwargs):
        if 'exc_info' not in kwargs:
            kwargs['exc_info'] = True
        super().error(msg, *args, **kwargs)


class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "level": record.levelname,
            "time": self.formatTime(record, self.datefmt),
            "message": record.getMessage(),
            "logger": record.name,
        }
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_record, ensure_ascii=False)


class AsyncLogger:
    def __init__(self, service_name: str, log_level: int, max_queue_size: int = 100):
        self.logger = setup_base_logger(service_name, log_level)
        self.log_queue = asyncio.Queue(max_queue_size)
        self.executor = ThreadPoolExecutor()
        self.log_level = log_level
        self.log_methods = {
            'error': self.logger.error,
            'warning': self.logger.warning,
            'info': self.logger.info,
            'debug': self.logger.debug
        }
        self._ensure_queue_processing()

    def _ensure_queue_processing(self):
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        loop.create_task(self._process_log_queue())

    async def _log_message(self, level: str, msg: str, *args, **kwargs):
        if self.log_queue.full():
            await self._process_log_queue()  # Process all messages if the queue is full
        if self.log_queue.full():  # Recheck if the queue is still full after processing
            if level in ['info', 'debug']:  # Drop info and debug logs if queue is still full
                return  # Dropping the log message
        await self.log_queue.put((level, msg, args, kwargs))

    async def _process_log_queue(self):
        while True:
            level, msg, args, kwargs = await self.log_queue.get()
            log_method: Callable = self.log_methods.get(level)
            if log_method:
                log_method(msg, *args, **kwargs)
            self.log_queue.task_done()

    def error(self, msg: str, *args, **kwargs):
        if self.log_level <= logging.ERROR:
            loop = asyncio.get_running_loop()
            asyncio.run_coroutine_threadsafe(self._log_message('error', msg, *args, **kwargs), loop)

    def info(self, msg: str, *args, **kwargs):
        if self.log_level <= logging.INFO:
            loop = asyncio.get_running_loop()
            asyncio.run_coroutine_threadsafe(self._log_message('info', msg, *args, **kwargs), loop)

    def debug(self, msg: str, *args, **kwargs):
        if self.log_level <= logging.DEBUG:
            loop = asyncio.get_running_loop()
            asyncio.run_coroutine_threadsafe(self._log_message('debug', msg, *args, **kwargs), loop)

    def warning(self, msg: str, *args, **kwargs):
        if self.log_level <= logging.WARNING:
            loop = asyncio.get_running_loop()
            asyncio.run_coroutine_threadsafe(self._log_message('warning', msg, *args, **kwargs), loop)

    def print_queue_length(self):
        """Print the current length of the log queue."""
        print(f"Log queue length: {self.log_queue.qsize()}")


def setup_base_logger(service_name: str, log_level: int, use_json: bool) -> Logger:
    logging.setLoggerClass(CustomLogger)
    # Creating and Setting Logger object and level
    logger_object = logging.getLogger(service_name)
    logger_object.setLevel(log_level)

    # Creating Handler object and set level
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    if use_json:
        formatter = JsonFormatter(datefmt='%m/%d/%Y %H:%M:%S')
    else:
        # Creating Formatter object and setting formatter object to handler
        formatter = logging.Formatter('\n%(levelname)s - %(asctime)s - %(message)s\n', datefmt='%m/%d/%Y %H:%M:%S')

    console_handler.setFormatter(formatter)
    # Adding Handler to Logger
    logger_object.addHandler(console_handler)

    return logger_object


def setup_sync_logger(service_name: str, log_level: int, use_json: bool) -> Logger:
    return setup_base_logger(service_name, log_level, use_json)


def setup_async_logger(service_name: str, log_level: int, use_json: bool) -> AsyncLogger:
    return AsyncLogger(service_name, log_level, use_json)


def get_log_level_from_string(level_str: str) -> int:
    """Convert a log level string to a logging level int."""
    level_str = level_str.upper()
    levels = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    return levels.get(level_str, logging.ERROR)


# Map log types to whether JSON logging should be used
log_type_map = {
    'json': True,
    'console': True
}


def setup_logger(service_name: str, async_mode: bool = False, log_level_str: str = 'DEBUG', log_type: str = 'json') -> \
Union[Logger, AsyncLogger]:
    use_json = log_type_map.get(log_type.lower(), False)  # default to console/text
    log_level = get_log_level_from_string(log_level_str)

    if async_mode:
        return setup_async_logger(service_name, log_level, use_json)
    else:
        return setup_sync_logger(service_name, log_level, use_json)

# async def check():
#     # Example of setting up a synchronous logger with a specific log level
#     logger = setup_logger("my_service", async_mode=False, log_level_str='INFO')
#     logger.info("This is an info sync message")
#     logger.debug("This debug message will not be shown because the log level is set to INFO")
#
#     # Example of setting up an asynchronous logger with a specific log level
#     async_logger = setup_logger("my_service_async", async_mode=True, log_level_str='ERROR')
#     async_logger.info("This info message will not be shown because the log level is set to WARNING")
#     async_logger.print_queue_length()
#     async_logger.warning("This is a warning async message")
#     async_logger.debug("This is a debug async message")
#     async_logger.print_queue_length()
#     async_logger.info("This is a debug info message")
#     async_logger.error("This is the error message", exc_info=False)
#     async_logger.print_queue_length()
#     try:
#         10 / 0
#     except ZeroDivisionError as e:
#         async_logger.error("This is an error message with an exception", exc_info=e)
#     await asyncio.sleep(1)


# if __name__ == "__main__":
#     asyncio.run(check())
