import asyncio
from os.path import join, dirname

import binance
from dotenv import load_dotenv

from discord_scraper import DiscordScraper
from misc.console import log, error
from ticker import Ticker
from trader import Trader

TAG = "MAIN"


async def main():
    dotenv_path = join(dirname(__file__), '../.env')
    load_dotenv(dotenv_path)

    trader = Trader()
    trader.start()
    client = trader.client
    market = trader.market
    asyncio.ensure_future(trader.thread())

    discord_scraper = DiscordScraper(asyncio.get_running_loop())
    discord_scraper.start()

    locked = False
    abort_if_best_ask_is_over_x_of_moving_average = 1.1
    sell_at_x_of_moving_average = 1.2

    while True:
        ticker_name = await discord_scraper.wait_for_next_ticker()
        if locked:
            log(TAG, f"Locked. Skipping current ticker...")
            continue
        log(TAG, f"Starting program sequence. Target ticker: {ticker_name}")
        t: Ticker = market[ticker_name]

        btc_balance = trader.balances["BTC"]
        log(TAG, f"Current BTC balance: {btc_balance}")

        buy_price = t.best_ask_price
        if buy_price is None:
            locked = True
            error(TAG, "Unable to fetch best ask price. Aborting...")
            continue
        log(TAG, f"Current best ask price is {buy_price:.16f}.")

        moving_average = t.moving_average
        buy_price_to_moving_average = buy_price / moving_average
        log(TAG, f"Moving average is {moving_average:.16f}")
        if buy_price_to_moving_average > abort_if_best_ask_is_over_x_of_moving_average:
            locked = True
            error(TAG, f"Best ask price is {buy_price_to_moving_average}x the moving average, "
                       f"> {abort_if_best_ask_is_over_x_of_moving_average}x! Aborting...")
            continue
        log(TAG, f"BeDumped Protection passed! "
                 f"Best ask price is {buy_price_to_moving_average}x the moving average.")

        buy_price = buy_price + t.quote_step * 1
        log(TAG, f"Adjusting buy price to {buy_price:.16f}.")

        sell_at_x_of_buy_price = moving_average * sell_at_x_of_moving_average / buy_price
        log(TAG, f"Selling at {sell_at_x_of_buy_price:.3f}x the buying price.")
        sell_price = t.best_ask_price * sell_at_x_of_buy_price / (1 - t.trading_fee) / (1 - t.trading_fee)

        buy_quantity = t.floor(btc_balance / buy_price)
        sell_quantity = t.floor(buy_quantity * (1 - t.trading_fee))

        buy_price_str = t.quote_truncate(buy_price)
        sell_price_str = t.quote_truncate(sell_price)

        log(TAG, f"Buying {buy_quantity:.16f} "
                 f"at {buy_price_str} "
                 f"for {buy_quantity * float(buy_price_str):.16f} "
                 f"and selling {sell_quantity:.16f} "
                 f"at {sell_price_str} "
                 f"for {sell_quantity * float(sell_price_str):.16f}")

        if buy_price < t.min_notional or sell_price < t.min_notional:
            locked = True
            error(TAG, f"Buy price or sell price is out of valid range.")
            continue

        if buy_quantity < t.min_qty or buy_quantity > t.max_qty or \
                sell_quantity < t.min_qty or sell_quantity > t.max_qty:
            locked = True
            error(TAG, f"Buy quantity or sell quantity is out of valid range.")
            continue

        buy_order = client.order_limit_buy(symbol=t.symbol,
                                           quantity=str(buy_quantity),
                                           price=buy_price_str)
        log(TAG, buy_order)
        while buy_order["status"] != "FILLED":
            log(TAG, buy_order["orderId"])
            await asyncio.sleep(.1)
            try:
                if client.get_order(symbol=t.symbol, orderId=buy_order["orderId"])["status"] == "FILLED":
                    break
            except binance.client.BinanceAPIException as ex:
                log(TAG, ex)
        log(TAG, "Buying filled")

        sell_order = client.order_limit_sell(symbol=t.symbol,
                                             quantity=str(sell_quantity),
                                             price=sell_price_str)
        log(TAG, sell_order)
        while sell_order["status"] != "FILLED":
            await asyncio.sleep(.1)
            log(TAG, sell_order["orderId"])
            try:
                if client.get_order(symbol=t.symbol, orderId=sell_order["orderId"])["status"] == "FILLED":
                    break
            except binance.client.BinanceAPIException as ex:
                log(TAG, ex)
        log(TAG, "Selling filled")

        locked = True
        log(TAG, "Program sequence completed. Re-locked.")


if __name__ == "__main__":
    asyncio.run(main())
