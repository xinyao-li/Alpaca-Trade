import threading

import alpaca_trade_api as tradeapi
from inputs import config
import logging
import time
import datetime

class CryptoData:
    logger = logging.getLogger('my_logger')
    # set the logging level to INFO
    logger.setLevel(logging.INFO)
    # create a file handler that writes logs to a file named logs.txt
    handler = logging.FileHandler('./analysis/price_data.txt')
    logger.addHandler(handler)

    # Instantiate REST API Connection
    api = tradeapi.REST(key_id=config.API_KEY, secret_key=config.SECRET_KEY, base_url=config.BASE_URL, api_version='v2')
    account = api.get_account()
    def data_retrieve(self,ticker,should_stop):
        list = []
        list.append(ticker)
        prev_bid_price = self.api.get_latest_crypto_quotes(list, "us")[ticker].bp
        prev_ask_price = self.api.get_latest_crypto_quotes(list, "us")[ticker].ap
        self.logger.info('bid_price:' + str(prev_bid_price))
        self.logger.info('ask_price:' + str(prev_ask_price))

        while not should_stop.is_set():
            bid_price = self.api.get_latest_crypto_quotes(list, "us")[ticker].bp
            ask_price = self.api.get_latest_crypto_quotes(list, "us")[ticker].ap
            if prev_ask_price != ask_price:
                self.logger.info('ask_price:' + str(ask_price))
                prev_ask_price = ask_price
            if prev_bid_price != bid_price:
                self.logger.info('bid_price:' + str(bid_price))
                prev_bid_price = bid_price

            time.sleep(1)

    def run_trade(self, ticker):
        #Create a new thread to execute grid_trading
        should_stop = threading.Event()
        thread = threading.Thread(target=self.data_retrieve(ticker, should_stop))
        thread.start()
        thread.join()

if __name__ == '__main__':
    should_stop = threading.Event()
    current_time = datetime.datetime.now()
    crypt_data = CryptoData()
    print('data collection start:')
    crypt_data.logger.info(current_time)
    crypt_data.run_trade('BTC/USD')