import sys
sys.path.append('/inputs')

import threading

import alpaca_trade_api as tradeapi
from inputs import config, variable
import logging
import time

class CryptoTrade:
    logger = logging.getLogger('my_logger')
    # set the logging level to INFO
    logger.setLevel(logging.INFO)
    # create a file handler that writes logs to a file named logs.txt
    handler = logging.FileHandler('logs.txt')
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

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
    def grid_trading(self, ticker, high, low, percentage, buying_power_percentage,should_stop):
        #Get the buying power from account
        buying_power = float(self.account.buying_power)
        total_profit = buying_power
        ticker_for_holding = ticker.replace('/','')
        holding_amount = self.api.get_position(ticker_for_holding).qty

        #Intialize the last trade price to close price of previous open date
        list = []
        list.append(ticker)
        last_trade_price = variable.last_trade_price

        self.logger.info('buying power is: '+ str(buying_power))
        self.logger.info('last trade price is: ' + str(last_trade_price))
        self.logger.info('holding amount is: ' + str(holding_amount))

        if last_trade_price is not None:
            while not should_stop.is_set():
                #get the current price of ticker in Binance in every 1 sec
                bid_price = None
                ask_price = None
                try:
                    bid_price = self.api.get_latest_crypto_quotes(list, "us")[ticker].bp
                    ask_price = self.api.get_latest_crypto_quotes(list, "us")[ticker].ap
                    print("bid price is: " + str(bid_price))
                    print("ask price is: "+str(ask_price))
                except Exception as e:
                    print('last trade price is: '+str(last_trade_price))
                    logging.exception("No such ticker or fail to get price")

                #If the price is in range low to high, if the price drop 'percentage' then buy, else if price reach 'percentage' then sell
                #Buy or Sell amount will be buy_power_percentage of buying power divided by current price of ticker.
                if bid_price is not None and ask_price is not None and ask_price <= high and bid_price >= low:
                    if ask_price <= last_trade_price*(1 - percentage):
                        try:
                            buying_amount = buying_power*buying_power_percentage/ask_price
                            self.api.submit_order(ticker, buying_amount, 'buy', 'market', time_in_force='gtc')
                            self.logger.info("Bought " + str(buying_amount) + " of "+str(ticker)+" at price: "+str(ask_price))

                            #Update the last_trade_price and holding_amount
                            last_trade_price = ask_price
                            holding_amount = self.api.get_position(ticker_for_holding).qty
                            self.writeValue('/inputs/variable.py',last_trade_price,holding_amount)
                            buying_power = float(self.account.buying_power)
                        except Exception as e:
                            logging.exception("Buy Order submission failed")

                        self.logger.info('last trade price is: ' + str(last_trade_price))

                    elif bid_price >= last_trade_price*(1 + percentage):
                        try:
                            selling_amount = buying_power * buying_power_percentage / bid_price
                            if holding_amount < selling_amount:
                                selling_amount = holding_amount
                            if selling_amount > 0:
                                self.api.submit_order(ticker, selling_amount, 'sell', 'market', time_in_force='gtc')
                                self.logger.info("Sold " + str(selling_amount) + " of " + str(ticker) + " at price: " + str(bid_price))

                            # Update the last_trade_price and holding_amount
                            last_trade_price = bid_price
                            holding_amount = self.api.get_position(ticker_for_holding).qty
                            self.writeValue('/inputs/variable.py', last_trade_price, holding_amount)
                            buying_power = float(self.account.buying_power)
                        except Exception as e:
                            logging.exception("Sell Order submission failed")

                        self.logger.info('last trade price is: ' + str(last_trade_price))
                        #print('total earn is: $' + str(buying_power - total_profit + holding_amount * last_trade_price))
                time.sleep(1)
            print('total profit in % is: ' + str((buying_power - total_profit + holding_amount * last_trade_price) / total_profit * 100) + '%')

    def run_trade(self, ticker, high, low, percentage, buying_power_percentage):
        #Create a new thread to execute grid_trading
        should_stop = threading.Event()
        thread = threading.Thread(target=self.grid_trading(ticker, high, low, percentage, buying_power_percentage, should_stop))
        thread.start()
        thread.join()

    def writeValue(self,doc,last_trade_price,holding_amount):
        with open(doc, 'w') as f:
            f.write(f'last_trade_price={last_trade_price}\n')
        print('New Value has updated')


if __name__ == '__main__':
    crypt_trade = CryptoTrade()
    print("grid trading start")
    crypt_trade.run_trade('BTC/USD',32000,26000,0.001,0.1)

