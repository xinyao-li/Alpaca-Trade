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
    target_price = 24000.00
    cash = 7033.13
    qty = 3.479762814
    percentage = 0.002
    buy_percentage = 0.1
    threshold = 4
    last_trade_price = 25542.7
    buy_balance = 3

    test(target_price,cash,qty,percentage,buy_percentage,threshold,last_trade_price,buy_balance)