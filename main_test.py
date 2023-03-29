import alpaca_trade_api as tradeapi
import config
import pandas as pd
import logging
import time

class CryptoTradeTest:
    # Instantiate REST API Connection
    api = tradeapi.REST(key_id=config.API_KEY, secret_key=config.SECRET_KEY, base_url=config.BASE_URL, api_version='v2')

    def grid_trading(self, ticker, high, low, percentage, buying_power,buying_power_percentage, data):

        #Intialize the last trade price as current price
        last_trade_price = float(data.iloc[len(data)-1][2].replace(',',''))

        for i, row in reversed(list(enumerate(data.itertuples(), start=1))):
            #get the current price of ticker in Binance in every 1 sec
            cur_price = None
            try:
                cur_price = float(data.iloc[i][2].replace(',',''))
            except Exception as e:
                logging.info("Failed to get the current price")
            #If the price is in range low to high, if the price drop 'percentage' then buy, else if price reach 'percentage' then sell
            #Buy or Sell amount will be buy_power_percentage of buying power divided by current price of ticker.
            if cur_price is not None and cur_price <= high and cur_price >= low:
                if cur_price <= last_trade_price*(1 - percentage):
                    try:
                        buying_amount = buying_power * buying_power_percentage / cur_price
                        print(f"Bought {buying_amount} of {ticker} at price: {cur_price}")
                        last_trade_price = cur_price
                        buying_power -= buying_amount * cur_price
                    except Exception as e:
                        logging.exception("Buy Order submission failed")
                elif cur_price >= last_trade_price*(1 + percentage):
                    try:
                        selling_amount = buying_power * buying_power_percentage / cur_price
                        print(f"Sold {selling_amount} of {ticker} at price: {cur_price}")
                        last_trade_price = cur_price
                        buying_power += selling_amount * cur_price
                    except Exception as e:
                        logging.exception("Sell Order submission failed")
                time.sleep(1)

if __name__ == '__main__':
    crypt_trade_test = CryptoTradeTest()
    print("grid trading start")
    data = pd.read_csv('data/Bitcoin-20220308-20230308.csv')
    crypt_trade_test.grid_trading('BTCUSD',50000,10000,0.0001,100000,0.1,data)

