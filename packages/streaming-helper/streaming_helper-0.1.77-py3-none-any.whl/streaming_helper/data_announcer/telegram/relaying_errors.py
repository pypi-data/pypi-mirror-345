# -*- coding: utf-8 -*-

# built ins
import asyncio

# installed
import orjson

# user defined formula
from streaming_helper.restful_api.telegram import (
    end_point_params_template as end_point_telegram,
)
from streaming_helper.restful_api import connector
from streaming_helper.utilities import system_tools


async def telegram_messaging(
    client_redis: object,
    client_id: str,
    client_secret: str,
) -> None:
    """ """

    try:

        # connecting to redis pubsub
        pubsub: object = client_redis.pubsub()

        error_channel: str = "error"

        # prepare channels placeholders
        channels = [
            error_channel,
        ]

        # subscribe to channels
        [await pubsub.subscribe(o) for o in channels]

        connection_url_telegram = end_point_telegram.basic_https()

        while True:

            try:

                message_byte = await pubsub.get_message()

                if message_byte and message_byte["type"] == "message":

                    message_byte_data = orjson.loads(message_byte["data"])

                    message_channel = message_byte["channel"]

                    if error_channel in message_channel:

                        data = message_byte_data["params"]["data"]

                        await connector.get_connected(
                            connection_url_telegram,
                            None,
                            client_id,
                            client_secret,
                            data,
                        )

            except Exception as error:

                await system_tools.parse_error_message_with_redis(
                    client_redis,
                    error,
                )

                continue

            finally:
                await asyncio.sleep(0.001)

    except Exception as error:

        await system_tools.parse_error_message_with_redis(
            client_redis,
            error,
        )
