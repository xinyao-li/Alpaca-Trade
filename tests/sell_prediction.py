import alpaca_trade_api as tradeapi
from inputs import config

api = tradeapi.REST(key_id=config.API_KEY, secret_key=config.SECRET_KEY, base_url=config.BASE_URL, api_version='v2')
def test(target_price,cash,qty,percentage,sell_percentage,threshold,last_trade_price,sell_balance):

    while last_trade_price * (1 + percentage) < target_price:
        last_trade_price *= (1 + percentage)
        if sell_balance > threshold:
            sell_balance = 1
        if qty - sell_percentage * cash * sell_balance / last_trade_price <= 0:
            break
        qty -= sell_percentage * cash * sell_balance / last_trade_price
        cash += sell_percentage * cash * sell_balance
        sell_balance += 1

    print("Current price: " + str(last_trade_price))
    print("Qty: " + str(qty))
    print("Cash: " + str(cash))
    print("Expected Properties in target price: " + str(qty * target_price + cash))
    print("Average Entry Price: " + str((100000 - cash) / qty))

if __name__ == '__main__':
    target_price = 27887.37
    cash = 11816.85
    qty = 3.252066876
    percentage = 0.002
    sell_percentage = 0.03
    threshold = 4
    last_trade_price = 27268.4
    sell_balance = 3

    test(target_price, cash, qty, percentage, sell_percentage, threshold, last_trade_price, sell_balance)


