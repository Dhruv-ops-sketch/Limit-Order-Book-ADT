# really simple (and slow) version of the order book.
# no heaps or dicts, it just loops over every resting order to find the best one.
# it's only here so the tests have something to compare the real one against


class ReferenceBook:
    def __init__(self):
        self.resting = []   # list of dicts
        self.counter = 0    # arrival order, for time priority
        self.trades = []

    def submit(self, order_id, side, qty, price=None):
        while qty > 0:
            best = None
            for o in self.resting:
                if o["side"] == side:
                    continue
                if price is not None:
                    if side == "buy" and o["price"] > price:
                        continue
                    if side == "sell" and o["price"] < price:
                        continue
                if best is None or self._better(o, best, side):
                    best = o

            if best is None:
                break

            fill = min(qty, best["qty"])
            qty -= fill
            best["qty"] -= fill
            if side == "buy":
                self.trades.append((order_id, best["id"], best["price"], fill))
            else:
                self.trades.append((best["id"], order_id, best["price"], fill))

            if best["qty"] == 0:
                self.resting.remove(best)

        if qty > 0 and price is not None:
            self.resting.append({"id": order_id, "side": side, "qty": qty,
                                 "price": price, "time": self.counter})
            self.counter += 1

    def _better(self, a, b, incoming_side):
        # buyers want the lowest ask, sellers want the highest bid.
        # if prices tie, whoever got there first wins
        if a["price"] != b["price"]:
            if incoming_side == "buy":
                return a["price"] < b["price"]
            return a["price"] > b["price"]
        return a["time"] < b["time"]

    def cancel(self, order_id):
        for o in self.resting:
            if o["id"] == order_id:
                self.resting.remove(o)
                return True
        return False
