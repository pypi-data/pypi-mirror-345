# -*- coding: utf-8 -*-

# built ins
import asyncio

# installed
from dataclassy import dataclass

# user defined formula
from streaming_helper.utilities import time_modification as time_mod
from streaming_helper.restful_api import connector


def get_basic_https() -> str:
    return f"https://www.deribit.com/api/v2/"


def get_currencies_end_point() -> str:
    return f"public/get_currencies?"

async def get_currencies() -> str:
    return await connector.get_connected(
            get_basic_https(),
            get_currencies_end_point(),
        )

def get_server_time_end_point() -> str:
    return f"public/get_time?"


def get_instruments_end_point(currency) -> str:
    return f"public/get_instruments?currency={currency.upper()}"

async def get_instruments(currency) -> str:
    return await connector.get_connected(
            get_basic_https(),
            get_instruments_end_point(currency),
        )


def get_tickers_end_point(instrument_name: str) -> str:

    return f"public/ticker?instrument_name={instrument_name}"


async def get_ticker(instrument_name: str) -> list:
    return await connector.get_connected(
            get_basic_https(),
            get_tickers_end_point(instrument_name),
        )

def get_tradingview_chart_data_end_point() -> str:
    return f"get_tradingview_chart_data?"


def get_ohlc_end_point(
    endpoint_tradingview: str,
    instrument_name: str,
    resolution: int,
    qty_or_start_time_stamp: int,
    provided_end_timestamp: int = None,
    qty_as_start_time_stamp: bool = False,
) -> str:

    now_unix = time_mod.get_now_unix_time()

    # start timestamp is provided
    start_timestamp = qty_or_start_time_stamp

    # recalculate start timestamp using qty as basis point
    if qty_as_start_time_stamp:
        start_timestamp = now_unix - (60000 * resolution) * qty_as_start_time_stamp

    if provided_end_timestamp:
        end_timestamp = provided_end_timestamp
    else:
        end_timestamp = now_unix

    return f"{endpoint_tradingview}end_timestamp={end_timestamp}&instrument_name={instrument_name}&resolution={resolution}&start_timestamp={start_timestamp}"


def get_json_payload(
    endpoint: str,
    params: dict,
) -> dict:

    id = id_numbering(
        endpoint,
        endpoint,
    )

    return {
        "jsonrpc": "2.0",
        "id": id,
        "method": f"{endpoint}",
        "params": params,
    }


def get_open_orders_end_point() -> str:
    return f"private/get_open_orders"


def get_open_orders_params(
    kind: str,
    type: str,
) -> dict:
    return {
        "kind": kind,
        "type": type,
    }


def get_subaccounts_end_point() -> str:
    return f"private/get_subaccounts"


def get_subaccounts_params(
    with_portfolio: bool = True,
) -> dict:
    return {
        "with_portfolio": with_portfolio,
    }


def get_subaccounts_details_end_point() -> str:
    return f"private/get_subaccounts_details"


def get_subaccounts_details_params(
    currency: str,
    with_open_orders: bool = True,
) -> dict:
    return {
        "currency": currency,
        "with_open_orders": with_open_orders,
    }

def get_end_point_based_on_side(side: str) -> str:

    if side == "buy":
        return "private/buy"

    if side == "sell":
        return "private/sell"



@dataclass(unsafe_hash=True, slots=True)
class SendApiRequest:
    """ """

    client_id: str
    client_secret: str
    
    
    async def get_open_orders(
        self,
        kind: str,
        type: str,  
        ):

        result = await connector.get_connected(
            get_basic_https(),
            get_open_orders_end_point(),
            self.client_id,
            self.client_secret,
            get_open_orders_params(
                kind, 
                type,
                )
        ) 

        return result

    
    async def get_subaccounts(
    self,
    with_portfolio: bool = True
    ) -> list:
    
        sub_account = await connector.get_connected(
        get_basic_https(),
        get_subaccounts_end_point(),
        self.client_id,
        self.client_secret,
        get_subaccounts_params(with_portfolio))

        return sub_account["result"]
    
    
    async def get_subaccounts_details(
    self,
    currency: str,
    with_open_orders: bool = True
    ) -> list:
    
        """

        currency= BTC/ETH
        example= https://www.deribit.com/api/v2/private/get_subaccounts_details?currency=BTC&with_open_orders=true


        result_sub_account["result"]

        Returns example:

         [
             {
                'positions': [
                     {
                         'estimated_liquidation_price': None,
                         'size_currency': -0.031537551,
                         'total_profit_loss': -0.005871738,
                         'realized_profit_loss': 0.0,
                         'floating_profit_loss': -0.002906191,
                         'leverage': 25,
                         'average_price': 74847.72,
                         'delta': -0.031537551,
                         'mark_price': 88783.05,
                         'settlement_price': 81291.98,
                         'instrument_name': 'BTC-15NOV24',
                         'index_price': 88627.96,
                         'direction': 'sell',
                         'open_orders_margin': 0.0,
                         'initial_margin': 0.001261552,
                         'maintenance_margin': 0.000630801,
                         'kind': 'future',
                         'size': -2800.0
                     },
                     {
                         'estimated_liquidation_price': None,
                         'size_currency': -0.006702271,
                         'total_profit_loss': -0.001912148,
                         'realized_profit_loss': 0.0,
                         'floating_profit_loss': -0.000624473,
                         'leverage': 25,
                         'average_price': 69650.67,
                         'delta': -0.006702271,
                         'mark_price': 89521.9,
                         'settlement_price': 81891.77,
                         'instrument_name': 'BTC-29NOV24',
                         'index_price': 88627.96,
                         'direction': 'sell',
                         'open_orders_margin': 0.0,
                         'initial_margin': 0.000268093,
                         'maintenance_margin': 0.000134048,
                         'kind': 'future',
                         'size': -600.0
                     },
                     {
                         'estimated_liquidation_price': None,
                         'size_currency': 0.036869785,
                         'realized_funding': -2.372e-05,
                         'total_profit_loss': 0.005782196,
                         'realized_profit_loss': 0.000591453,
                         'floating_profit_loss': 0.002789786,
                         'leverage': 50,
                         'average_price': 76667.01,
                         'delta': 0.036869785,
                         'interest_value': 0.2079087278497569,
                         'mark_price': 88690.51,
                         'settlement_price': 81217.47,
                         'instrument_name': 'BTC-PERPETUAL',
                         'index_price': 88627.96,
                         'direction': 'buy',
                         'open_orders_margin': 3.489e-06,
                         'initial_margin': 0.000737464,
                         'maintenance_margin': 0.000368766,
                         'kind': 'future',
                         'size': 3270.0
                     }
                     ],

                'open_orders': [
                     {
                         'is_liquidation': False,
                         'risk_reducing': False,
                         'order_type': 'limit',
                         'creation_timestamp': 1731390729846,
                         'order_state': 'open',
                         'reject_post_only': False,
                         'contracts': 1.0,
                         'average_price': 0.0,
                         'reduce_only': False,
                         'post_only': True,
                         'last_update_timestamp': 1731390729846,
                         'filled_amount': 0.0,
                         'replaced': False,
                         'mmp': False,
                         'web': False,
                         'api': True,
                         'instrument_name': 'BTC-PERPETUAL',
                         'amount': 10.0,
                         'order_id': '80616245864',
                         'max_show': 10.0,
                         'time_in_force': 'good_til_cancelled',
                         'direction': 'buy',
                         'price': 88569.5,
                         'label': 'hedgingSpot-closed-1731387973670'
                     }
                     ],

                'uid': 148510
                }
        ]

        """

        sub_account = await connector.get_connected(
        get_basic_https(),
        get_subaccounts_details_end_point(),
        self.client_id,
        self.client_secret,
        get_subaccounts_details_params(
        currency,
        with_open_orders,
        ))

        return sub_account["result"]
    
    async def get_transaction_log(
        self,
        currency: str,
        start_timestamp: int,
        count: int = 1000,
        query: str = "trade",
    ) -> list:
        """
        query:
            trade, maker, taker, open, close, liquidation, buy, sell,
            withdrawal, delivery, settlement, deposit, transfer,
            option, future, correction, block_trade, swap

        """


        result_transaction_log_to_result = await connector.get_connected(
        get_basic_https(),
        get_transaction_log_end_point(),
        self.client_id,
        self.client_secret,
        get_transaction_log_params(
        currency,
        start_timestamp,
        count,
        query,
        ))


        try:
            result = result_transaction_log_to_result["result"]

            return [] if not result else result["logs"]

        except:

            error = result_transaction_log_to_result["error"]
            
            message = error["message"]
            
            return message

    async def get_cancel_order_all(
        self,
        detailed: bool = False
        ):

        # Set endpoint
        endpoint: str = "private/cancel_all"

        params = {"detailed": False}


        result = await connector.get_connected(
        get_basic_https(),
        cancel_all_orders_end_point(),
        self.client_id,
        self.client_secret,
        cancel_all_orders_params(detailed))

        return result


    async def get_cancel_order_byOrderId(
        self,
        order_id: str,
    ) -> None:
        # Set endpoint

        result = await connector.get_connected(
        get_basic_https(),
        cancel_order_end_point(),
        self.client_id,
        self.client_secret,
        get_cancel_order_params(order_id))

        return result


    async def send_order(
        self,
        side: str,
        instrument,
        amount,
        label: str = None,
        price: float = None,
        type: str = "limit",
        otoco_config: list = None,
        linked_order_type: str = None,
        trigger_price: float = None,
        trigger: str = "last_price",
        time_in_force: str = "fill_or_kill",
        reduce_only: bool = False,
        post_only: bool = True,
        reject_post_only: bool = False,
    ) -> None:

        params = {}

        params.update({"instrument_name": instrument})
        params.update({"amount": amount})
        params.update({"label": label})
        params.update({"instrument_name": instrument})
        params.update({"type": type})

        if trigger_price is not None:

            params.update({"trigger": trigger})
            params.update({"trigger_price": trigger_price})
            params.update({"reduce_only": reduce_only})

        if "market" not in type:
            params.update({"price": price})
            params.update({"post_only": post_only})
            params.update({"reject_post_only": reject_post_only})

        if otoco_config:
            params.update({"otoco_config": otoco_config})

            if linked_order_type is not None:
                params.update({"linked_order_type": linked_order_type})
            else:
                params.update({"linked_order_type": "one_triggers_other"})

            params.update({"trigger_fill_condition": "incremental"})

            log.debug(f"params otoco_config {params}")

        result = None

        if side is not None:

            endpoint: str = get_end_point_based_on_side(side)

            result = await private_connection(
                self.sub_account_id,
                endpoint=endpoint,
                params=params,
            )

        return result

    async def get_open_orders(
        self,
        kind: str,
        type: str,
    ) -> list:

        # Set endpoint
        endpoint: str = "private/get_open_orders"

        params = {"kind": kind, "type": type}

        result_open_order = await private_connection(
            self.sub_account_id,
            endpoint=endpoint,
            params=params,
        )

        return result_open_order["result"]

    async def send_limit_order(
        self,
        params: dict,
    ) -> None:
        """ """

        # basic params
        log.info(f"params {params}")
        side = params["side"]
        instrument = params["instrument_name"]
        label_numbered = params["label"]
        size = params["size"]
        type = params["type"]
        limit_prc = params["entry_price"]

        try:
            otoco_config = params["otoco_config"]
        except:
            otoco_config = None

        try:
            linked_order_type = params["linked_order_type"]

        except:
            linked_order_type = None

        order_result = None

        if side != None:

            if type == "limit":  # limit has various state

                order_result = await self.send_order(
                    side,
                    instrument,
                    size,
                    label_numbered,
                    limit_prc,
                    type,
                    otoco_config,
                )

            else:

                trigger_price = params["trigger_price"]
                trigger = params["trigger"]

                order_result = await self.send_order(
                    side,
                    instrument,
                    size,
                    label_numbered,
                    limit_prc,
                    type,
                    otoco_config,
                    linked_order_type,
                    trigger_price,
                    trigger,
                )

        # log.warning(f"order_result {order_result}")

        if order_result != None and (
            "error" in order_result or "message" in order_result
        ):

            error = order_result["error"]
            message = error["message"]

            try:
                data = error["data"]
            except:
                data = message

            await tlgrm.telegram_bot_sendtext(
                f"message: {message}, \
                                         data: {data}, \
                                         (params: {params}"
            )

        log.warning(f"order_result {order_result}")
        return order_result
    
def get_user_trades_by_currency_end_point() -> str:
    return f"private/get_user_trades_by_currency"


def get_user_trades_by_currency_params(
    currency: str,
    kind: str = "any",
    count: int = 1000,
) -> dict:
    return {
        "currency": currency,
        "kind": kind,
        "count": count,
    }


def get_user_trades_by_instrument_and_time_end_point() -> str:
    return f"private/get_user_trades_by_instrument_and_time"


def get_user_trades_by_instrument_and_time_params(
    instrument_name: str,
    start_timestamp: int,
    count: int = 1000,
) -> dict:

    now_unix = time_mod.get_now_unix_time()

    return {
        "count": count,
        "end_timestamp": now_unix,
        "instrument_name": instrument_name,
        "start_timestamp": start_timestamp,
    }


def get_transaction_log_end_point() -> str:
    return f"private/get_transaction_log"


def get_transaction_log_params(
    currency: str,
    start_timestamp: int,
    count: int = 1000,
    query: str = "trade",
) -> dict:

    now_unix = time_mod.get_now_unix_time()

    return {
        "count": count,
        "currency": currency,
        "end_timestamp": now_unix,
        "query": query,
        "start_timestamp": start_timestamp,
    }


def send_orders_end_point(params: dict) -> str:

    return f"private/{params["side"]}"


def send_orders_params(
    side: str,
    instrument,
    amount,
    label: str = None,
    price: float = None,
    type: str = "limit",
    otoco_config: list = None,
    linked_order_type: str = None,
    trigger_price: float = None,
    trigger: str = "last_price",
    time_in_force: str = "fill_or_kill",
    reduce_only: bool = False,
    post_only: bool = True,
    reject_post_only: bool = False,
) -> str:

    params = {}

    params.update({"instrument_name": instrument})
    params.update({"amount": amount})
    params.update({"label": label})
    params.update({"instrument_name": instrument})
    params.update({"type": type})

    if trigger_price is not None:

        params.update({"trigger": trigger})
        params.update({"trigger_price": trigger_price})
        params.update({"reduce_only": reduce_only})

    if "market" not in type:
        params.update({"price": price})
        params.update({"post_only": post_only})
        params.update({"reject_post_only": reject_post_only})

    if otoco_config:
        params.update({"otoco_config": otoco_config})

        if linked_order_type is not None:
            params.update({"linked_order_type": linked_order_type})
        else:
            params.update({"linked_order_type": "one_triggers_other"})

        params.update({"trigger_fill_condition": "incremental"})

    return params


def send_limit_order_params(
    params: dict,
) -> str:
    """ """

    # basic params
    side = params["side"]
    instrument = params["instrument_name"]
    label_numbered = params["label"]
    size = params["size"]
    type = params["type"]
    limit_prc = params["entry_price"]

    try:
        otoco_config = params["otoco_config"]
    except:
        otoco_config = None

    try:
        linked_order_type = params["linked_order_type"]

    except:
        linked_order_type = None

    order_result = None

    if side != None:

        if type == "limit":  # limit has various state

            order_result = send_orders_params(
                side,
                instrument,
                size,
                label_numbered,
                limit_prc,
                type,
                otoco_config,
            )

        else:

            trigger_price = params["trigger_price"]
            trigger = params["trigger"]

            order_result = send_orders_params(
                side,
                instrument,
                size,
                label_numbered,
                limit_prc,
                type,
                otoco_config,
                linked_order_type,
                trigger_price,
                trigger,
            )

    return order_result


def cancel_all_orders_end_point() -> str:
    return f"private/cancel_all"

def cancel_all_orders_params() -> dict:
    return {"detailed": False}


def cancel_order_end_point() -> str:
    return f"private/cancel"


def get_cancel_order_params(
    order_id: str,
) -> dict:

    return {"order_id": order_id}


def get_api_end_point(
    endpoint: str,
    parameters: dict = None,
) -> dict:
    """
    used in data receiver deribit

    """

    private_endpoint = f"private/{endpoint}"

    params = {}
    params.update({"jsonrpc": "2.0"})
    params.update({"method": private_endpoint})
    if endpoint == "get_subaccounts":
        params.update({"params": {"with_portfolio": True}})

    if endpoint == "get_open_orders":
        end_point_params = dict(kind=parameters["kind"], type=parameters["type"])

        params.update({"params": end_point_params})

    return params


def id_numbering(
    operation: str,
    ws_channel: str,
) -> str:
    """

    id convention

    method
    subscription    3
    get             4

    auth
    public	        1
    private	        2

    instruments
    all             0
    btc             1
    eth             2

    subscription
    --------------  method      auth    seq    inst
    portfolio	        3	    1	    01
    user_order	        3	    1	    02
    my_trade	        3	    1	    03
    order_book	        3	    2	    04
    trade	            3	    1	    05
    index	            3	    1	    06
    announcement	    3	    1	    07

    get
    --------------
    currencies	        4	    2	    01
    instruments	        4	    2	    02
    positions	        4	    1	    03

    """
    id_auth = 1
    if "user" in ws_channel:
        id_auth = 9

    id_method = 0
    if "subscribe" in operation:
        id_method = 3
    if "get" in operation:
        id_method = 4
    id_item = 0
    if "book" in ws_channel:
        id_item = 1
    if "user" in ws_channel:
        id_item = 2
    if "chart" in ws_channel:
        id_item = 3
    if "index" in ws_channel:
        id_item = 4
    if "order" in ws_channel:
        id_item = 5
    if "position" in ws_channel:
        id_item = 6
    id_instrument = 0
    if "BTC" or "btc" in ws_channel:
        id_instrument = 1
    if "ETH" or "eth" in ws_channel:
        id_instrument = 2
    return int(f"{id_auth}{id_method}{id_item}{id_instrument}")
