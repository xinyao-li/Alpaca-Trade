#Draft code, will be removed after the model has done.
import sys
sys.path.append('../inputs')

import alpaca_trade_api as tradeapi

from inputs import config, variable

api = tradeapi.REST(key_id=config.API_KEY, secret_key=config.SECRET_KEY, base_url=config.BASE_URL, api_version='v2')
account = api.get_account()
x = 1
list = []
list.append('BTC/USD')
position = api.get_position('BTCUSD')

def test():
    histpd = {}
    for pd in ['1D', '2D', '3D', '7D']:
        hist = api.get_portfolio_history(period=pd,
        extended_hours=True,
        timeframe='1Min').df
        histpd[pd] = hist
        print(histpd)

if __name__ == '__main__':
    test()
