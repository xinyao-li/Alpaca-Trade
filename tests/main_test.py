import alpaca_trade_api as tradeapi
from alpaca_trade_api import TimeFrame
from inputs import config
import pandas as pd
import logging
import matplotlib.pyplot as plt

class CryptoTradeTest:
    # Instantiate REST API Connection
    api = tradeapi.REST(key_id=config.API_KEY, secret_key=config.SECRET_KEY, base_url=config.BASE_URL, api_version='v2')

    def grid_trading(self, ticker, high, low, percentage, buying_power,buying_power_percentage, start,end,high_standard,low_standard):
        tickers = []
        tickers.append(ticker)
        data = self.api.get_crypto_bars(tickers, '1Min', start, end).df
        #print(data)

        #Intialize the last trade price as current price
        last_trade_price = float(data.iloc[0]['high'])
        total_profit = buying_power
        holding_amount = 0
        result = []
        market_high = []
        market_low = []

        for i, row in list(enumerate(data.itertuples(), start=0)):
            #get the current price of ticker in Binance in every 1 sec
            high_price = None
            low_price = None

            try:
                high_price = float(data.iloc[i]['high'])
                low_price =  float(data.iloc[i]['high'])
            except Exception as e:
                logging.info("Failed to get the current price")

            #If the price is in range low to high, if the price drop 'percentage' then buy, else if price reach 'percentage' then sell
            #Buy or Sell amount will be buy_power_percentage of buying power divided by current price of ticker.
            if high_price is not None and low_price is not None and high_price <= high and low_price >= low:
                if high_price <= last_trade_price*(1 - percentage):
                    try:
                        buying_amount = buying_power * buying_power_percentage / high_price
                        print(f"Bought {buying_amount} of {ticker} at price: {high_price}")
                        last_trade_price = high_price
                        buying_power -= buying_amount * high_price
                        holding_amount += buying_amount
                    except Exception as e:
                        logging.exception("Buy Order submission failed")
                    print('total earn is: $' + str(buying_power - total_profit + holding_amount * last_trade_price))
                elif low_price >= last_trade_price*(1 + percentage):
                    try:
                        selling_amount = buying_power * buying_power_percentage / low_price
                        if holding_amount < selling_amount:
                            selling_amount = holding_amount
                        print(f"Sold {selling_amount} of {ticker} at price: {low_price}")
                        last_trade_price = low_price
                        buying_power += selling_amount * low_price
                        holding_amount -= selling_amount
                    except Exception as e:
                        logging.exception("Sell Order submission failed")
                    print('total earn is: $' + str(buying_power - total_profit + holding_amount * last_trade_price))
                #time.sleep(1)
            elif low_price is not None and low_price > high and low_price <= high + high_standard:
                if holding_amount > 0:
                    buying_power += holding_amount * low_price
                    holding_amount = 0.0
                    last_trade_price = low_price
                    print('Sold all amount')
            elif high_price is not None and high_price < low and high_price >= low - low_standard:
                buying_amount = buying_power * buying_power_percentage * 2 / high_price
                buying_power -= buying_amount * high_price
                holding_amount += buying_amount
                last_trade_price = high_price
                print(f"Bought {buying_amount} of {ticker} at price: {high_price}")
            try:
                result.append([str(data.iloc[i][0]), low_price, (buying_power - total_profit + holding_amount * last_trade_price)/total_profit*100])
                if i > 0:
                    market_high.append([str(data.iloc[i][0]),low_price,(float(data.iloc[i]['high']) - float(data.iloc[i - 1]['high']))/float(data.iloc[i]['high'])*100])
                    market_low.append([str(data.iloc[i][0]), low_price,(float(data.iloc[i]['low']) - float(data.iloc[i - 1]['low'])) / float(data.iloc[i]['low']) * 100])
            except Exception as e:
                logging.exception("")
        print('total profit in % is: '+str((buying_power - total_profit + holding_amount * last_trade_price)/total_profit*100)+'%')
        new_data = pd.DataFrame(result, columns=['date', 'close_price', 'total_profit'])
        market_high_data = pd.DataFrame(market_high, columns=['date', 'close_price', 'total_profit'])
        market_low_data = pd.DataFrame(market_low, columns=['date', 'close_price', 'total_profit'])
        return new_data, market_high_data, market_low_data


if __name__ == '__main__':
    crypt_trade_test = CryptoTradeTest()
    print("grid trading start")
    stat_data = crypt_trade_test.grid_trading('BTC/USD',30168.7359,30037.43,0.0001,100000,0.3,'2023-04-13','2023-04-14',182.044,140.864)
    plt.figure(figsize=(16, 8))
    #print(stat_data[0])

    # Plot the close_price and total_profit
    plt.plot(stat_data[0]['date'], stat_data[0]['total_profit'], label='Grid Trade Profit')
    plt.plot(stat_data[1]['date'], stat_data[1]['total_profit'], label='Market Profit in High')
    plt.plot(stat_data[2]['date'], stat_data[2]['total_profit'], label='Market Profit in Low')


    # Set the title, labels and legend
    plt.title('Bitcoin market regression tests Feb 2023')
    plt.xlabel('Date', fontsize=18)
    plt.ylabel('Total profit in %', fontsize=18)
    plt.legend()

    # Show the plot
    plt.show()

