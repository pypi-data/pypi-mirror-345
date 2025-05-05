import asyncio
import json
import logging
from typing import Optional, Union

import aiohttp
import requests


def add_extra_properties_to_schema(schema, appsettings_path):
    # Load the appsettings.json file
    with open(appsettings_path, 'r') as appsettings_file:
        appsettings = json.load(appsettings_file)

    # Initialize the extra properties dictionary
    extra_properties = {}

    # Mapping of Python types to JSON schema types
    type_mapping = {
        'str': 'string',
        'int': 'integer',
        'float': 'number',
        'bool': 'boolean',
        'list': 'array',
        'dict': 'object',
        'NoneType': 'null'
    }

    # Add properties from appsettings to the extra dictionary if not in schema
    for key, value in appsettings.items():
        if key not in schema['properties']:
            json_type = type_mapping.get(type(value).__name__, 'string')
            extra_properties[key] = {"type": json_type}

    # Add the extra properties to the schema
    if extra_properties:
        schema['properties']['extra'] = {
            "type": "object",
            "properties": extra_properties
        }

    return schema


class SingletonMeta(type):
    """
    This is a thread-safe implementation of Singleton.
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class GoogleChatSyncMessenger(metaclass=SingletonMeta):
    def __init__(self, service_name: str, g_chat_webhook: str, g_chat_error_webhook: str, environ: str,
                 log_enabled: Optional[list] = None,
                 logger: Optional[logging.Logger] = None):
        if log_enabled is None:
            log_enabled = ['production']

        self.service_name = service_name
        self.g_chat_webhook = g_chat_webhook
        if g_chat_error_webhook:
            self.g_chat_error_webhook = g_chat_error_webhook
        else:
            self.g_chat_error_webhook = g_chat_webhook
        self.environ = environ
        self.log_enabled = log_enabled
        self.logger = logger
        self.color_dict = {
            1: '#008000',  # Green
            0: '#FF0000',  # Red
        }

    def send_message(self, text_message: str, message_type: int = None):
        """Send message to Google Chat synchronously."""
        try:
            message_headers = {'Content-Type': 'application/json; charset=UTF-8'}

            # Check if the environment is enabled for logging
            if self.environ not in self.log_enabled:
                return

            # Determine color based on message type
            color = self.color_dict.get(message_type, '#000000')  # Default to black if unknown type
            if message_type == 0:
                url = self.g_chat_error_webhook
            else:
                url = self.g_chat_webhook
            bot_message = {
                "cards": [
                    {
                        "header": {
                            "title": f"*{self.service_name}*",
                            "subtitle": f"_{self.environ}_"
                        },
                        "sections": [
                            {
                                "widgets": [
                                    {
                                        "textParagraph": {
                                            "text": f"<font color='{color}'>{text_message}</font>"
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }

            response = requests.post(
                url=url,
                headers=message_headers,
                data=json.dumps(bot_message),
            )
            response.raise_for_status()  # Raise an HTTPError if the HTTP request returned an unsuccessful status code
        except Exception as e:
            self.logger.error('Error in webhookApi', exc_info=True)


class GoogleChatAsyncMessenger(metaclass=SingletonMeta):
    def __init__(self, service_name: str, g_chat_webhook: str, g_chat_error_webhook: str, environ: str,
                 log_enabled: Optional[list] = None,
                 logger: Optional[logging.Logger] = None, max_queue_size: int = 100):
        if log_enabled is None:
            log_enabled = ['PRODUCTION']
        if g_chat_error_webhook:
            self.g_chat_error_webhook = g_chat_error_webhook
        else:
            self.g_chat_error_webhook = g_chat_webhook

        self.service_name = service_name
        self.g_chat_webhook = g_chat_webhook

        self.environ = environ
        self.log_enabled = log_enabled
        self.logger = logger
        self.color_dict = {
            1: '#008000',  # Green
            0: '#FF0000',  # Red
        }
        self.log_queue = asyncio.Queue(max_queue_size)
        self.queue_task = None

    def _ensure_queue_processing(self):
        if not self.queue_task or self.queue_task.done():
            loop = asyncio.get_event_loop()
            self.queue_task = loop.create_task(self._process_log_queue())

    async def _enqueue_message(self, text_message: str, message_type: int):
        await self.log_queue.put((text_message, message_type))

    async def _process_log_queue(self):
        while True:
            text_message, message_type = await self.log_queue.get()
            await self._send_message_async(text_message, message_type)
            self.log_queue.task_done()

    def send_message(self, text_message: str, message_type: int = None):
        """Send message to Google Chat, either synchronously or asynchronously."""
        self._ensure_queue_processing()
        try:
            loop = asyncio.get_running_loop()
            asyncio.run_coroutine_threadsafe(self._enqueue_message(text_message, message_type), loop)
        except RuntimeError:
            # No running event loop, so create a new one for this sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self._enqueue_message(text_message, message_type))

    async def _send_message_async(self, text_message: str, message_type: int):
        """Send message to Google Chat asynchronously."""
        try:
            message_headers = {'Content-Type': 'application/json; charset=UTF-8'}

            # Check if the environment is enabled for logging
            if self.environ not in self.log_enabled:
                return

            # Determine color based on message type
            color = self.color_dict.get(message_type, '#000000')
            if message_type == 0:
                url = self.g_chat_error_webhook
            else:
                url = self.g_chat_webhook

            bot_message = {
                "cards": [
                    {
                        "header": {
                            "title": f"*{self.service_name}*",
                            "subtitle": f"_{self.environ}_"
                        },
                        "sections": [
                            {
                                "widgets": [
                                    {
                                        "textParagraph": {
                                            "text": f"<font color='{color}'>{text_message}</font>"
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                        url=url,
                        headers=message_headers,
                        data=json.dumps(bot_message),
                ) as response:
                    response.raise_for_status()  # Raise an HTTPError if the HTTP request returned an unsuccessful status code
        except Exception as e:
            self.logger.error('Error in webhookApi', exc_info=True)


def setup_google_chat_messenger(service_name: str, g_chat_webhook: str,
                                g_chat_error_webhook: str,
                                environ: str, async_mode: bool = False,
                                log_enabled: Optional[list] = None, logger: Optional[logging.Logger] = None) -> Union[
    GoogleChatSyncMessenger, GoogleChatAsyncMessenger]:
    if async_mode:
        return GoogleChatAsyncMessenger(service_name, g_chat_webhook, g_chat_error_webhook, environ, log_enabled,
                                        logger)
    else:
        return GoogleChatSyncMessenger(service_name, g_chat_webhook, g_chat_error_webhook, environ, log_enabled, logger)

# async def main():
#     async_messenger = GoogleChatAsyncMessenger(
#         service_name="AsyncService",
#         g_chat_webhook="https://chat.googleapis.com/v1/spaces/AAAAdbgldrA/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=djR15znKwDBQMzv2sGcHBbBSh60KvXbtYgdIBzM_5a8",
#         environ="production",
#         log_enabled=['production'],
#         logger=logging.getLogger("async_logger")
#     )
#
#     async_messenger.send_message(
#         text_message="Hello from async!",
#         message_type=1,
#     )
#     # await asyncio.sleep(1)
#
#
# if __name__ == "__main__":
#     sync_messenger = GoogleChatSyncMessenger(
#         service_name="SyncService",
#         g_chat_webhook="https://chat.googleapis.com/v1/spaces/AAAAdbgldrA/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=djR15znKwDBQMzv2sGcHBbBSh60KvXbtYgdIBzM_5a8",
#         environ="production",
#         log_enabled=['production'],
#         logger=logging.getLogger("sync_logger")
#     )
#
#     sync_messenger.send_message(
#         text_message="Hello from sync!",
#         message_type=0,
#     )
#
#     asyncio.run(main())
