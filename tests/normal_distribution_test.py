import alpaca_trade_api as tradeapi
from alpaca_trade_api import TimeFrame

from inputs import config

class DistributionTest:
    # Instantiate REST API Connection
    api = tradeapi.REST(key_id=config.API_KEY, secret_key=config.SECRET_KEY, base_url=config.BASE_URL, api_version='v2')
    def normal_distribution_fit(self,ticker,start,end):
        tickers = []
        tickers.append(ticker)
        data = self.api.get_crypto_bars(tickers, TimeFrame.Hour, start, end).df
        high_sum = 0
        low_sum = 0
        count = 0
        for i, row in list(enumerate(data.itertuples(), start=0)):
            high_sum += float(data.iloc[i]['high'])
            low_sum += float(data.iloc[i]['low'])
            count += 1

        high_mean = high_sum/count
        low_mean = low_sum/count
        high_standard = 0
        low_standard = 0

        for i, row in list(enumerate(data.itertuples(), start=0)):
            high_standard += (float(data.iloc[i]['high']) - high_mean)**2
            low_standard += (float(data.iloc[i]['low']) - low_mean)**2

        high_standard = (high_standard/count)**(1/2)
        low_standard = (low_standard/count)**(1/2)
        map_high = {}
        map_low = {}
        map_high['mean'] = 0
        map_low['mean'] = 0
        map_high['1s'] = 0
        map_low['1s'] = 0
        map_high['2s'] = 0
        map_low['2s'] = 0
        map_high['3s'] = 0
        map_low['3s'] = 0
        map_high['-1s'] = 0
        map_low['-1s'] = 0
        map_high['-2s'] = 0
        map_low['-2s'] = 0
        map_high['-3s'] = 0
        map_low['-3s'] = 0
        for i, row in list(enumerate(data.itertuples(), start=0)):
            high = float(data.iloc[i]['high'])
            low =  float(data.iloc[i]['low'])
            if high == high_mean:
                 map_high['mean']+= 1
            if high > high_mean and high <= high_mean + high_standard:
                map_high['1s']+=1
            if high > high_mean + high_standard and high <= high_mean + 2 * high_standard:
                map_high['2s']+=1
            if high > high_mean + 2 * high_standard and high <= 3 * high_standard:
                map_high['3s']+=1
            if high < high_mean and high >= high_mean - high_standard:
                map_high['-1s']+=1
            if high < high_mean - high_standard and high >= high_mean - 2 * high_standard:
                map_high['-2s'] += 1
            if high < high_mean - 2 * high_standard and high >= high_mean - 3 * high_standard:
                map_high['-3s'] += 1
            if low == low_mean:
                map_low['mean']+= 1
            if low > low_mean and low <= low_mean + low_standard:
                map_low['1s']+=1
            if low > low_mean + low_standard and low <= low_mean + 2 * low_standard:
                map_low['2s']+=1
            if low > low_mean + 2 * low_standard and low <= 3 * low_standard:
                map_low['3s']+=1
            if low < low_mean and low >= low_mean - low_standard:
                map_low['-1s'] += 1
            if low < low_mean - low_standard and low >= low_mean - 2 * low_standard:
                map_low['-2s'] += 1
            if low < low_mean - 2 * low_standard and low >= low_mean - 3 * low_standard:
                map_low['-3s'] += 1

        map_high['mean'] = map_high['mean']/count * 100
        map_high['1s'] = map_high['1s']/count * 100
        map_high['2s'] = map_high['2s']/count * 100
        map_high['3s'] = map_high['2s']/count * 100
        map_high['-1s'] = map_high['-1s'] / count * 100
        map_high['-2s'] = map_high['-2s'] / count * 100
        map_high['-3s'] = map_high['-2s'] / count * 100
        map_low['mean'] = map_low['mean'] / count * 100
        map_low['1s'] = map_low['1s'] / count * 100
        map_low['2s'] = map_low['2s'] / count * 100
        map_low['3s'] = map_low['2s'] / count * 100
        map_low['-1s'] = map_low['-1s'] / count * 100
        map_low['-2s'] = map_low['-2s'] / count * 100
        map_low['-3s'] = map_low['-2s'] / count * 100

        print(map_high)
        print(map_low)

        print("high_mean:"+str(high_mean))
        print("low_mean:"+str(low_mean))
        print(high_mean - high_standard)
        print(low_mean - low_standard)



if __name__ == '__main__':
    distribution_test = DistributionTest()
    distribution_test.normal_distribution_fit('BTC/USD','2023-04-07','2023-04-14')

