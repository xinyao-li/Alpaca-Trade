import alpaca_trade_api as tradeapi
import config
import pandas as pd
import logging
import time
import matplotlib.pyplot as plt

class CryptoTradeTest:
    # Instantiate REST API Connection
    api = tradeapi.REST(key_id=config.API_KEY, secret_key=config.SECRET_KEY, base_url=config.BASE_URL, api_version='v2')

    def grid_trading(self, ticker, high, low, percentage, buying_power,buying_power_percentage, data):

        #Intialize the last trade price as current price
        last_trade_price = float(data.iloc[len(data)-1][2].replace(',',''))
        total_profit = buying_power
        holding_amount = 0
        result = []

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
                        holding_amount += buying_amount
                    except Exception as e:
                        logging.exception("Buy Order submission failed")
                    print('total earn is: $' + str(buying_power - total_profit + holding_amount * last_trade_price))
                elif cur_price >= last_trade_price*(1 + percentage):
                    try:
                        selling_amount = buying_power * buying_power_percentage / cur_price
                        if holding_amount < selling_amount:
                            selling_amount = holding_amount
                        print(f"Sold {selling_amount} of {ticker} at price: {cur_price}")
                        last_trade_price = cur_price
                        buying_power += selling_amount * cur_price
                        holding_amount -= selling_amount
                    except Exception as e:
                        logging.exception("Sell Order submission failed")
                    print('total earn is: $' + str(buying_power - total_profit + holding_amount * last_trade_price))
                #time.sleep(1)
            try:
                result.append([str(data.iloc[i][1]), cur_price, (buying_power - total_profit + holding_amount * last_trade_price)/total_profit*100])
            except Exception as e:
                logging.exception("")
        print('total profit in % is: '+str((buying_power - total_profit + holding_amount * last_trade_price)/total_profit*100)+'%')
        new_data = pd.DataFrame(result, columns=['date', 'close_price', 'total_profit'])
        return new_data


if __name__ == '__main__':
    crypt_trade_test = CryptoTradeTest()
    print("grid trading start")
    data = pd.read_csv('data/Bitcoin-20220308-20230308.csv')
    new_data = crypt_trade_test.grid_trading('BTCUSD',50000,10000,0.0001,100000,0.01,data)
    plt.figure(figsize=(16, 8))

    # Plot the close_price and total_profit
    plt.plot(new_data['date'], new_data['total_profit'], label='Total Profit')

    # Set the title, labels and legend
    plt.title('Bitcoin market regression test Feb 2023')
    plt.xlabel('Date', fontsize=18)
    plt.ylabel('Total profit in %', fontsize=18)
    plt.legend()

    # Show the plot
    plt.show()

