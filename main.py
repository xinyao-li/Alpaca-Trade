import threading

import alpaca_trade_api as tradeapi
import config
import datetime as dt
import logging
import time

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
    def grid_trading(self, ticker, high, low, percentage, buying_power_percentage, should_stop):
        #Get the buying power from account
        buying_power = float(self.account.buying_power)
        total_profit = buying_power
        holding_amount = config.holding_amount

        #Intialize the last trade price to close price of previous open date
        last_trade_price = config.last_trade_price
        print('last trade price is: ' + str(last_trade_price))
        print('holding amount is: ' + str(holding_amount))

        if last_trade_price is not None:
            while not should_stop.is_set():
                #get the current price of ticker in Binance in every 1 sec
                cur_price = None
                try:
                    cur_price = self.api.get_latest_crypto_trade(ticker, 'BNCU').price
                    print("current price is: " + str(cur_price))
                except Exception as e:
                    print('last trade price is: '+last_trade_price)
                    logging.exception("No such ticker or fail to get price")

                #If the price is in range low to high, if the price drop 'percentage' then buy, else if price reach 'percentage' then sell
                #Buy or Sell amount will be buy_power_percentage of buying power divided by current price of ticker.
                if cur_price is not None and cur_price <= high and cur_price >= low:
                    if cur_price <= last_trade_price*(1 - percentage):
                        try:
                            buying_amount = buying_power*buying_power_percentage/cur_price
                            self.api.submit_order(ticker, buying_amount, 'buy', 'market', time_in_force='gtc')
                            print("Bought " + str(buying_amount) + " of "+str(ticker)+" at price: "+str(cur_price))
                            last_trade_price = cur_price
                            print('last trade price is: ' + str(last_trade_price))
                            buying_power = float(self.account.buying_power)
                            holding_amount += buying_amount
                        except Exception as e:
                            print('last trade price is: ' + str(last_trade_price))
                            logging.exception("Buy Order submission failed")
                        print('total earn is: $' + str(buying_power - total_profit + holding_amount * last_trade_price))
                    elif cur_price >= last_trade_price*(1 + percentage):
                        try:
                            selling_amount = buying_power * buying_power_percentage / cur_price
                            if holding_amount < selling_amount:
                                selling_amount = holding_amount
                            if selling_amount > 0:
                                self.api.submit_order(ticker, selling_amount, 'sell', 'market', time_in_force='gtc')
                                print("Sold " + str(selling_amount) + " of " + str(ticker) + " at price: " + str(cur_price))
                            last_trade_price = cur_price
                            print('last trade price is: ' + str(last_trade_price))
                            buying_power = float(self.account.buying_power)
                            holding_amount -= selling_amount
                        except Exception as e:
                            print('last trade price is: ' + str(last_trade_price))
                            logging.exception("Sell Order submission failed")
                        print('total earn is: $' + str(buying_power - total_profit + holding_amount * last_trade_price))
                time.sleep(1)
            print('total profit in % is: ' + str((buying_power - total_profit + holding_amount * last_trade_price) / total_profit * 100) + '%')

    def run_trade(self, ticker, high, low, percentage, buying_power_percentage):
        #Create a new thread to execute grid_trading
        should_stop = threading.Event()
        thread = threading.Thread(target=self.grid_trading(ticker, high, low, percentage, buying_power_percentage, should_stop))
        thread.start()
        thread.join()


if __name__ == '__main__':
    crypt_trade = CryptoTrade()
    print("grid trading start")
    crypt_trade.run_trade('BTCUSD',30000,26000,0.001,0.1)

