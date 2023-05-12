import threading

import alpaca_trade_api as tradeapi
from inputs import config, variable, parameter
from analysis import normal_distribution
import logging
import datetime
import time

class CryptoTrade:
    # create a logger for record trading history
    logger1 = logging.getLogger('my_logger1')
    logger1.setLevel(logging.INFO)
    handler = logging.FileHandler('logs.txt')
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger1.addHandler(handler)

    # create a logger for record bid and ask price
    logger2 = logging.getLogger('my_logger2')
    logger2.setLevel(logging.INFO)
    handler2 = logging.FileHandler('./analysis/price_data.txt')
    handler2.setLevel(logging.INFO)
    logger2.addHandler(handler2)

    # Instantiate REST API Connection
    api = tradeapi.REST(key_id=config.API_KEY, secret_key=config.SECRET_KEY, base_url=config.BASE_URL, api_version='v2')
    seconds = variable.seconds
    last_trade_price = variable.last_trade_price
    holding_amount = None

    # Function to generate a list of all bought trade you made and sort by buy in price
    def grid_trading(self, ticker, high, low, percentage, buying_power_percentage,bid_standard,ask_standard,period):
        # Get the buying power from account
        self.buying_power = float(self.api.get_account().buying_power)
        ticker_for_holding = ticker.replace('/','')
        try:
            self.holding_amount = float(self.api.get_position(ticker_for_holding).qty)
        except Exception as e:
            self.holding_amount = 0

        # Intialize the last trade price to close price of previous open date
        list = []
        list.append(ticker)

        self.logger1.info('buying power is: '+ str(self.buying_power))
        self.logger1.info('last trade price is: ' + str(self.last_trade_price))
        self.logger1.info('holding amount is: ' + str(self.holding_amount))

        if self.last_trade_price is not None:
            while self.seconds < period:
                # Get the current price of ticker in Binance in every 1 sec
                bid_price = None
                ask_price = None
                try:
                    bid_price = self.api.get_latest_crypto_quotes(list, "us")[ticker].bp
                    ask_price = self.api.get_latest_crypto_quotes(list, "us")[ticker].ap
                    #print("bid price is: " + str(bid_price))
                    #print("ask price is: "+str(ask_price))
                    self.logger2.info('ask_price:' + str(ask_price))
                    self.logger2.info('bid_price:' + str(bid_price))

                except Exception as e:
                    print('last trade price is: '+str(self.last_trade_price))
                    logging.exception("No such ticker or fail to get price")

                # If the price is in range low to high, if the price drop 'percentage' then buy, else if price reach 'percentage' then sell
                # Buy or Sell amount will be buy_power_percentage of buying power divided by current price of ticker.
                if bid_price is not None and ask_price is not None and ask_price <= high and bid_price >= low:
                    if ask_price <= self.last_trade_price*(1 - percentage):
                        try:
                            buying_amount = self.buying_power*buying_power_percentage/ask_price
                            self.api.submit_order(ticker, buying_amount, 'buy', 'limit', time_in_force='gtc',limit_price=ask_price)
                            self.logger1.info("Bought " + str(buying_amount) + " of "+str(ticker)+" at price: "+str(ask_price))

                            #Update the last_trade_price and holding_amount
                            self.last_trade_price = ask_price
                            self.holding_amount = float(self.api.get_position(ticker_for_holding).qty)
                            self.writeValue('./inputs/variable.py',self.last_trade_price)
                            self.buying_power = float(self.api.get_account().buying_power)
                        except Exception as e:
                            self.logger1.exception("Buy Order submission failed")

                        self.logger1.info('last trade price is: ' + str(self.last_trade_price))

                    elif bid_price >= self.last_trade_price*(1 + percentage):
                        try:
                            selling_amount = self.buying_power * buying_power_percentage / bid_price
                            # corner case when sell_amount less than 2e-9
                            temp = str(selling_amount)
                            if temp.__contains__('e') and float(temp[len(temp) - 1]) >= 8:
                                if self.holding_amount > 0.000000002:
                                    selling_amount = self.buying_power / bid_price
                                else:
                                    selling_amount = 0

                            if self.holding_amount < selling_amount:
                                selling_amount = self.holding_amount
                                self.logger1.info('Not enough amount to sold')
                            if selling_amount > 0.000000002:
                                self.api.submit_order(ticker, selling_amount, 'sell', 'limit', time_in_force='gtc', limit_price=bid_price)
                                self.logger1.info("Sold " + str(selling_amount) + " of " + str(ticker) + " at price: " + str(bid_price))
                                self.holding_amount = float(self.api.get_position(ticker_for_holding).qty)

                            # Update the last_trade_price and holding_amount
                            self.last_trade_price = bid_price
                            self.writeValue('./inputs/variable.py', self.last_trade_price)
                            self.buying_power = float(self.api.get_account().buying_power)
                        except Exception as e:
                            self.logger1.exception("Sell Order submission failed")

                        self.logger1.info('last trade price is: ' + str(self.last_trade_price))

                # When bid price in range [high, high + ask_standard], sell half of current holding amount
                elif bid_price is not None and self.last_trade_price <= high and bid_price > high:
                    selling_amount = None
                    try:
                        selling_amount = self.buying_power * buying_power_percentage / bid_price
                    except Exception as e:
                        selling_amount = 0
                    # Corner case when sell_amount less than 2e-9
                    temp = str(selling_amount)
                    if temp.__contains__('e') and float(temp[len(temp)-1]) >= 8:
                        if self.holding_amount > 0.000000002:
                            selling_amount = self.buying_power / bid_price
                        else:
                            selling_amount = 0
                            self.logger1.info('Not enough amount to sold')

                    if selling_amount is not None and selling_amount > 0.000000002:
                        if float(self.api.get_position(ticker_for_holding).avg_entry_price) < bid_price:
                            selling_amount *= 2
                        try:
                            self.api.submit_order(ticker, selling_amount, 'sell', 'limit', time_in_force='gtc', limit_price=bid_price)
                            self.last_trade_price = bid_price
                            self.holding_amount = float(self.api.get_position(ticker_for_holding).qty)
                            self.buying_power = float(self.api.get_account().buying_power)
                            self.writeValue('./inputs/variable.py', self.last_trade_price)
                            self.logger1.info("Sold double amounts")
                        except Exception as e:
                            self.logger1.exception("Sell Double Order submission failed")

                        self.logger1.info('last trade price is: ' + str(self.last_trade_price))

                time.sleep(1)
                self.seconds += 1
                self.writeValue('./inputs/variable.py',self.last_trade_price)

    def dynamic_trade(self, ticker, percentage, buying_power_percentage, period, should_stop):
        while not should_stop.is_set():
            self.logger2.info(datetime.datetime.now())
            distribution = normal_distribution.Distribution()
            result = distribution.distribution_cal('./analysis/price_data.txt')
            self.grid_trading(ticker,result[0],result[1],percentage,buying_power_percentage,result[2],result[3],period)
            self.seconds = 0
            self.writeValue('./inputs/variable.py',self.last_trade_price)

    def run_trade(self, ticker, percentage, buying_power_percentage,period):
        #Create a new thread to execute grid_trading
        should_stop = threading.Event()
        thread = threading.Thread(target=self.dynamic_trade(ticker, percentage, buying_power_percentage, period, should_stop))
        thread.start()
        thread.join()

    def writeValue(self,doc,last_trade_price):
        with open(doc, 'w') as f:
            f.write(f'last_trade_price={last_trade_price}\n')
            f.write(f'seconds={self.seconds}\n')


if __name__ == '__main__':
    crypt_trade = CryptoTrade()
    print("grid trading start")
    crypt_trade.run_trade(parameter.ticker,parameter.percentage,parameter.buying_power_percentage,parameter.period)