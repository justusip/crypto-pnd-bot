import asyncio
import os
import re
from threading import Thread

import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from misc.console import log

TAG = "DISCORD"


class DiscordScraper:
    def __init__(self, loop):
        self.tickers = []
        self.loop = loop
        self.thread = None
        self.on_ticker_detected_trigger = asyncio.Event()
        self.on_ticker_detected_ticker = None

    def load_tickers(self):
        log(TAG, "Fetching tickers...")
        self.tickers = list(
            o["symbol"] for o in requests.get("https://api.binance.com/api/v3/exchangeInfo").json()["symbols"]
        )
        log(TAG, f"{len(self.tickers)} tickers loaded.")

    def start(self):
        self.load_tickers()
        self.thread = Thread(target=self.scrape, args=())
        self.thread.start()

    async def wait_for_next_ticker(self):
        log(TAG, "Waiting for next ticker...")
        await self.on_ticker_detected_trigger.wait()
        self.on_ticker_detected_trigger.clear()
        return self.on_ticker_detected_ticker

    def scrape(self):
        discord_email = os.environ.get("DISCORD_EMAIL")
        discord_password = os.environ.get("DISCORD_PASSWORD")
        pnd_channel_url = os.environ.get("PND_CHANNEL_URL")

        login_btn_xpath = "/html/body/div[1]/div[2]/div/div[1]/div/div/div/div/form/div/div/div[1]/div[2]/button[2]"
        message_container_xpath = "/html/body/div/div[2]/div/div[2]/div/div/div/div[2]/div[2]/div[2]/main/div[1]/div/div/div"

        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
        driver.get(pnd_channel_url)
        WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH, login_btn_xpath)))

        # Initialize and input email
        username_input = driver.find_element_by_name("email")
        username_input.send_keys(discord_email)

        # Initialize and input password
        password_input = driver.find_element_by_name("password")
        password_input.send_keys(discord_password)

        # Initialize and login
        login_button = driver.find_element_by_xpath(login_btn_xpath)
        login_button.click()

        WebDriverWait(driver, 60).until(EC.visibility_of_element_located((By.XPATH, message_container_xpath)))
        log(TAG, f"Logged in.")

        message_container = driver.find_element_by_xpath(message_container_xpath)
        messages = message_container.find_elements_by_class_name("message-2qnXI6")

        def ticker_detected(msg):
            if (match := re.search("#([A-Za-z]+?)$", msg, re.MULTILINE)) is not None:
                ticker = match[1].upper() + "BTC"
                if ticker in self.tickers:
                    return ticker
            if (match := re.search("^([A-Za-z]+?) is looking perfect", msg,
                                   re.MULTILINE)) is not None:
                ticker = match[1].upper() + "BTC"
                if ticker in self.tickers:
                    return ticker
            return None

        for message in messages:
            if (ticker := ticker_detected(message.text)) is not None:
                log(TAG, f"Detected {ticker} from past messages.")

        while True:
            WebDriverWait(driver, 99999999).until(
                lambda x: len(message_container.find_elements_by_class_name("message-2qnXI6")) > len(messages))
            cur_messages = message_container.find_elements_by_class_name("message-2qnXI6")
            for cur_message in cur_messages:
                if cur_message not in messages:
                    msg = cur_message.text
                    if (ticker := ticker_detected(msg)) is not None:
                        log(TAG, f"Detected {ticker}!")
                        self.on_ticker_detected_ticker = ticker
                        self.loop.call_soon_threadsafe(self.on_ticker_detected_trigger.set)
                    messages.append(cur_message)
