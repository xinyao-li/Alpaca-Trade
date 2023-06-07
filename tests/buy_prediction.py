import alpaca_trade_api as tradeapi
from inputs import config

api = tradeapi.REST(key_id=config.API_KEY, secret_key=config.SECRET_KEY, base_url=config.BASE_URL, api_version='v2')
def test(target_price,cash,qty,percentage,buy_percentage,threshold,last_trade_price,buy_balance):

    while last_trade_price * (1 - percentage) > target_price:
        last_trade_price *= (1 - percentage)
        if buy_balance > threshold:
            buy_balance = 1
        if cash * buy_balance * buy_percentage / last_trade_price <= 0.000000002:
            break
        qty += buy_percentage * cash * buy_balance / last_trade_price
        cash -= buy_percentage * cash * buy_balance
        buy_balance += 1

    print("Current price: " + str(last_trade_price))
    print("Qty: " + str(qty))
    print("Cash: " + str(cash))
    print("Expected Properties in target price: " + str(qty * target_price + cash))
    print("Average Entry Price: " + str((100000-cash)/qty))

if __name__ == '__main__':
    target_price = 25000.37
    cash = 11816.85
    qty = 3.252066876
    percentage = 0.002
    buy_percentage = 0.03
    threshold = 4
    last_trade_price = 27268.4
    buy_balance = 2

    test(target_price,cash,qty,percentage,buy_percentage,threshold,last_trade_price,buy_balance)