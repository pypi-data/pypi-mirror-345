# -*- coding: utf-8 -*-

# built ins
import asyncio

# user defined formula
from streaming_helper.restful_api.telegram import (
    end_point_params_template as end_point_telegram,
)
from streaming_helper.channel_management import get_published_messages
from streaming_helper.utilities import system_tools


async def telegram_messaging(
    client_redis: object,
    client_id: str,
    client_secret: str,
    redis_channels: list,
) -> None:
    """ """

    try:

        # connecting to redis pubsub
        pubsub: object = client_redis.pubsub()

        error_channel: str = "error"

        # get redis channels
        order_rest_channel: str = redis_channels["order_rest"]
        my_trade_receiving_channel: str = redis_channels["my_trade_receiving"]
        order_update_channel: str = redis_channels["order_cache_updating"]
        portfolio_channel: str = redis_channels["portfolio"]
        sqlite_updating_channel: str = redis_channels["sqlite_record_updating"]
        sub_account_cached_channel: str = redis_channels["sub_account_cache_updating"]
        # prepare channels placeholders
        channels = [error_channel, my_trade_receiving_channel]

        # subscribe to channels
        [await pubsub.subscribe(o) for o in channels]

        while True:

            try:

                message_byte = await pubsub.get_message()

                params = await get_published_messages.get_redis_message(message_byte)

                data = params["data"]

                message_channel = params["channel"]

                if error_channel in message_channel:

                    await end_point_telegram.send_message(
                        client_id,
                        client_secret,
                        data,
                    )

                if my_trade_receiving_channel in message_channel:

                    for trade in data:

                        if trade:
                            instrument_name = trade["instrument_name"]
                            amount = trade["amount"]
                            price = trade["price"]
                            direction = trade["direction"]

                            text = f"Trade: {direction} {amount} of {instrument_name}  @ {price} "

                            await end_point_telegram.send_message(
                                client_id,
                                client_secret,
                                text,
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
