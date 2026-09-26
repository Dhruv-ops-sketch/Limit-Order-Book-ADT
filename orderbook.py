import heapq
from collections import deque


class Order:
    def __init__(self, order_id, side, qty, price=None):
        self.id = order_id
        self.side = side        # "buy" or "sell"
        self.qty = qty
        self.price = price      # None = market order
        self.cancelled = False

    def __repr__(self):
        return f"Order({self.id}, {self.side}, {self.qty} @ {self.price})"


class OrderBook:
    def __init__(self):
        # price -> deque of orders at that price, oldest at the front
        self.bids = {}
        self.asks = {}

        # heaps of prices so the best price is always on top.
        # heapq is a min heap so bid prices get stored as negatives
        self.bid_heap = []
        self.ask_heap = []

        # order id -> order, so cancel doesn't have to search for it
        self.orders = {}

        # every trade as (buy_id, sell_id, price, qty)
        self.trades = []

    def submit(self, order_id, side, qty, price=None):
        if order_id in self.orders:
            raise ValueError(f"order id {order_id} is already in the book")
        if side not in ("buy", "sell"):
            raise ValueError("side has to be buy or sell")
        if qty <= 0:
            raise ValueError("qty has to be positive")

        order = Order(order_id, side, qty, price)

        if side == "buy":
            self._match(order, self.asks, self.ask_heap, 1)
            if order.qty > 0 and price is not None:
                self._rest(order, self.bids, self.bid_heap, -1)
        else:
            self._match(order, self.bids, self.bid_heap, -1)
            if order.qty > 0 and price is not None:
                self._rest(order, self.asks, self.ask_heap, 1)

        # leftover market order qty just gets dropped
        return order

    def cancel(self, order_id):
        order = self.orders.pop(order_id, None)
        if order is None:
            return False
        # don't dig it out of the deque (that would be O(n)),
        # just mark it and skip it later when it reaches the front
        order.cancelled = True
        return True

    def best_bid(self):
        self._clean_top(self.bids, self.bid_heap, -1)
        return -self.bid_heap[0] if self.bid_heap else None

    def best_ask(self):
        self._clean_top(self.asks, self.ask_heap, 1)
        return self.ask_heap[0] if self.ask_heap else None

    def _match(self, order, levels, heap, sign):
        while order.qty > 0:
            self._clean_top(levels, heap, sign)
            if not heap:
                break

            best = heap[0] * sign
            # limit orders stop once the price is worse than their limit
            if order.price is not None:
                if order.side == "buy" and best > order.price:
                    break
                if order.side == "sell" and best < order.price:
                    break

            resting = levels[best][0]
            fill = min(order.qty, resting.qty)
            order.qty -= fill
            resting.qty -= fill

            if order.side == "buy":
                self.trades.append((order.id, resting.id, best, fill))
            else:
                self.trades.append((resting.id, order.id, best, fill))

            if resting.qty == 0:
                levels[best].popleft()
                del self.orders[resting.id]

    def _rest(self, order, levels, heap, sign):
        if order.price not in levels:
            levels[order.price] = deque()
            heapq.heappush(heap, order.price * sign)
        levels[order.price].append(order)
        self.orders[order.id] = order

    def _clean_top(self, levels, heap, sign):
        # get rid of cancelled orders and empty price levels at the top
        while heap:
            price = heap[0] * sign
            level = levels[price]
            while level and level[0].cancelled:
                level.popleft()
            if level:
                return
            del levels[price]
            heapq.heappop(heap)

    def show(self, depth=5):
        # just for printing, doesn't need to be fast
        def total(level):
            return sum(o.qty for o in level if not o.cancelled)

        asks = [(p, total(self.asks[p])) for p in sorted(self.asks)]
        bids = [(p, total(self.bids[p])) for p in sorted(self.bids, reverse=True)]
        asks = [a for a in asks if a[1] > 0][:depth]
        bids = [b for b in bids if b[1] > 0][:depth]

        print("   ASKS")
        for p, q in reversed(asks):
            print(f"  {p:>7}  {q:>5}")
        print("  " + "-" * 14)
        for p, q in bids:
            print(f"  {p:>7}  {q:>5}")
        print("   BIDS")
