class Hold:
    def __init__(self):
        self._symbol = None
        self._side = None
        self._qty = None
        self._filled_avg_price =None

    def set_symbol(self, symbol):
        self._symbol = symbol

    def get_symbol(self):
        return self._symbol

    def set_side(self,side):
        self._side = side

    def get_side(self):
        return self._side

    def set_qty(self,qty):
        self._qty = qty

    def get_qty(self):
        return self._qty

    def set_filled_avg_price(self,filled_avg_price):
        self._filled_avg_price = filled_avg_price

    def get_filled_avg_price(self):
        return self._filled_avg_price

