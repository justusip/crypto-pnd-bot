import math


class Ticker:
    def __init__(self, symbol, base_asset, quote_asset):
        self.symbol = symbol
        self.base_asset = base_asset
        self.quote_asset = quote_asset
        self.base_precision = None
        self.quote_step = None
        self.trading = False
        self.min_qty = None
        self.max_qty = None
        self.step_qty = None
        self.min_notional = None
        self.best_bid_price = None
        self.best_ask_price = None
        self.best_bid_quantity = None
        self.best_ask_quantity = None
        self.trading_fee = 0.001
        self.quote_volume = None
        self.best_bid_price_history = []
        self.best_bid_price_rising = None
        self.moving_average = None

    def floor(self, price: float):
        return math.floor(price / self.step_qty) * self.step_qty

    def ceil(self, price: float):
        return math.ceil(price / self.step_qty) * self.step_qty

    def quote_truncate(self, quote_price: float):
        return str(math.floor(quote_price / self.quote_step) * self.quote_step)
