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
print(api.get_position('BTCUSD').qty)
with open('variable.py', 'w') as f:
    f.write(f'last_trade_price={variable.last_trade_price}\n')
#    f.write(f'holding_amount={holding_amount}\n')
'''
while x > 0:
    bid_price = api.get_latest_crypto_quotes(list,"us")['BTC/USD'].bp
    ask_price = api.get_latest_crypto_quotes(list,"us")['BTC/USD'].ap
    print('bid price:'+str(bid_price))
    print('ask price:' + str(ask_price))
    api.submit_order('BTC/USD', 0.0001, 'buy', 'market', time_in_force='gtc')
    #print('bought')
    time.sleep(1)
'''