import threading

import alpaca_trade_api as tradeapi
import config
import datetime as dt
import logging
import time
from holds import Hold

class CryptoTrade:
    # Instantiate REST API Connection
    api = tradeapi.REST(key_id=config.API_KEY, secret_key=config.SECRET_KEY, base_url=config.BASE_URL, api_version='v2')
    account = api.get_account()
    '''
    #Download the data
    now = dt.datetime.today()
    now = now.strftime("%Y-%m-%d")
    data = api.get_crypto_bars('BTCUSD', tradeapi.rest.TimeFrame.Minute, now, now).df
    '''

    # Function to generate a list of all bought trade you made and sort by buy in price
    def calculate_buy_history(self, ticker):
        orders = self.api.list_orders(status='filled')
        order_list = []
        for order in orders:
            cur_hold = Hold()
            symbol = order.symbol.replace('/', '')
            if symbol == ticker and order.side == 'buy':
                cur_hold.set_symbol(symbol)
                cur_hold.set_qty(order.qty)
                cur_hold.set_filled_avg_price(order.filled_avg_price)
                order_list.append(cur_hold)
        order_list = sorted(order_list, key=lambda h: h._filled_avg_price, reverse=False)
        return order_list

    def grid_trading(self, ticker, high, low, percentage, buying_power_percentage, should_stop):
        #Get the buying power from account
        buying_power = float(self.account.buying_power)

        #intialize the last trade price as current price
        last_trade_price = self.api.get_latest_crypto_trade(ticker, 'BNCU').price

        if last_trade_price is not None:
            while not should_stop.is_set():
                #get the current price of ticker in Binance in every 1 sec
                cur_price = None
                try:
                    cur_price = self.api.get_latest_crypto_trade(ticker, 'BNCU').price
                    print("current price is: " + str(cur_price))
                except Exception as e:
                    logging.exception("No such ticker or fail to get price")

                #If the price is in range low to high, if the price drop 'percentage' then buy, else if price reach 'percentage' then sell
                #Buy or Sell amount will be buy_power_percentage of buying power divided by current price of ticker.
                if cur_price is not None and cur_price <= high and cur_price >= low:
                    if cur_price <= last_trade_price*(1 - percentage):
                        try:
                            self.api.submit_order(ticker, buying_power*buying_power_percentage/cur_price, 'buy', 'market', time_in_force='gtc')
                            print("Bought " + str(buying_power*buying_power_percentage/cur_price) + " of "+str(ticker)+" at price: "+str(cur_price))
                            last_trade_price = cur_price
                            buying_power = float(self.account.buying_power)
                        except Exception as e:
                            logging.exception("Buy Order submission failed")
                    elif cur_price >= last_trade_price*(1 + percentage):
                        try:
                            self.api.submit_order(ticker, buying_power*buying_power_percentage/cur_price, 'sell', 'market', time_in_force='gtc')
                            print("Sold " + str(buying_power*buying_power_percentage/cur_price) + " of " + str(ticker) + " at price: " + str(cur_price))
                            last_trade_price = cur_price
                            buying_power = float(self.account.buying_power)
                        except Exception as e:
                            logging.exception("Sell Order submission failed")
                time.sleep(1)

    def run_trade(self, ticker, high, low, percentage, buying_power_percentage):
        #Create a new thread to execute grid_trading
        should_stop = threading.Event()
        thread = threading.Thread(target=self.grid_trading(ticker, high, low, percentage, buying_power_percentage, should_stop))
        thread.start()
        thread.join()


if __name__ == '__main__':
    should_stop = threading.Event()
    crypt_trade = CryptoTrade()
    print("grid trading start")
    crypt_trade.run_trade('BTCUSD',28000,27000,0.0001,0.1)

