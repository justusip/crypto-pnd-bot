import asyncio
import os
from numbers import Number
from typing import Optional

import aiohttp
import binance
from aiohttp import ClientWebSocketResponse, WSMessage

from ticker import Ticker
from misc.console import *

TAG = "BINANCE"


class Trader:
    def __init__(self):
        self.market: {str: Ticker} = {}
        self.balances: {str: Number} = {}
        self.client = binance.Client(os.environ.get("BINANCE_API_KEY"), os.environ.get("BINANCE_API_SECRET"))
        self.ws: Optional[ClientWebSocketResponse] = None

    def start(self):
        info = self.client.get_exchange_info()["symbols"]
        for o in info:
            t = Ticker(o["symbol"], o["baseAsset"], o["quoteAsset"])
            t.base_precision = int(o["baseAssetPrecision"])
            # t.quote_precision = int(o["quoteAssetPrecision"])
            self.market[o["symbol"]] = t

            t.quote_step = float([f for f in o["filters"] if f["filterType"] == "PRICE_FILTER"][0]["tickSize"])

            t.trading = o["status"] == "TRADING"
            t.min_qty = float([f for f in o["filters"] if f["filterType"] == "LOT_SIZE"][0]["minQty"])
            t.max_qty = float([f for f in o["filters"] if f["filterType"] == "LOT_SIZE"][0]["maxQty"])
            t.step_qty = float([f for f in o["filters"] if f["filterType"] == "LOT_SIZE"][0]["stepSize"])
            t.min_notional = float([f for f in o["filters"] if f["filterType"] == "MIN_NOTIONAL"][0]["minNotional"])
        log(TAG, f"Loaded {len(self.market)} tickers.")

        self.balances = {o["asset"]: float(o["free"]) for o in self.client.get_account()["balances"]}
        log(TAG, f"Loaded {len(self.balances)} balances with non-zero wallets "
                 f"{', '.join([f'{k}: {v:.06f}' for (k, v) in self.balances.items() if v != 0])}")

    async def thread(self):
        while True:
            try:
                log(TAG, "Connecting to Binance's WebSocket market streams...")
                async with aiohttp.ClientSession() as session:
                    async with session.ws_connect(
                            'wss://stream.binance.com:9443/stream?streams=!bookTicker/!miniTicker@arr') as self.ws:
                        log(TAG, "Connected to Binance's WebSocket market streams.")
                        msg: WSMessage
                        async for msg in self.ws:
                            if msg.type == aiohttp.WSMsgType.TEXT:
                                data = msg.json()
                                if "stream" in data:
                                    if data["stream"] == "!bookTicker":
                                        payload = data["data"]
                                        ticker: Ticker = self.market[payload["s"]]
                                        ticker.best_bid_price = float(payload["b"])
                                        ticker.best_ask_price = float(payload["a"])
                                        ticker.best_bid_quantity = float(payload["B"])
                                        ticker.best_ask_quantity = float(payload["A"])
                                    elif data["stream"] == '!miniTicker@arr':
                                        payloads = data["data"]
                                        for payload in payloads:
                                            # dong zyu hai sin lmao
                                            ticker: Ticker = self.market[payload["s"]]
                                            ticker.moving_average = float(payload["o"])
                                else:
                                    print(data)

                            elif msg.type == aiohttp.WSMsgType.ERROR:
                                error(TAG, f"WebSocket connection was closed unexpectedly {self.ws.exception()}")
                                break
                log(TAG, "Disconnected from Binance's WebSocket market streams. Reconnecting...")
            except aiohttp.ClientError as ex:
                error(TAG, "Failed to connect to Binance's WebSocket market streams. "
                           f"Retrying in a second... ({ex})")
                await asyncio.sleep(1)
