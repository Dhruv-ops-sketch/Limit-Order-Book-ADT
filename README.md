# Limit Order Book & Matching Engine

A matching engine like the ones exchanges use, written in Python. It keeps a
book of buy orders (bids) and sell orders (asks) and matches incoming orders
against them using **price-time priority**: the best price goes first, and if
two orders have the same price, whoever got there first goes first.

It supports:
- limit orders (buy/sell at a price or better, leftover sits in the book)
- market orders (fill against whatever's there, leftover gets dropped)
- partial fills
- cancelling orders
- a log of every trade as `(buy_id, sell_id, price, qty)`

## Running it

No libraries needed except pytest for the tests.

```
python main.py
```

This runs a small demo and prints the book and the trades:

```
starting book:
   ASKS
      102      5
      101     18
  --------------
      100      3
       99      7
   BIDS
...
trades:
  buy #6 / sell #1: 10 @ 101
  buy #6 / sell #3: 2 @ 101
  buy #5 / sell #7: 3 @ 100
  buy #4 / sell #7: 2 @ 99
```

Using it in code:

```python
from orderbook import OrderBook

book = OrderBook()
book.submit(1, "sell", 10, 101)   # limit sell 10 @ 101
book.submit(2, "buy", 4, 101)     # limit buy 4 @ 101 -> trades with order 1
book.submit(3, "buy", 5)          # market buy 5
book.cancel(1)
print(book.trades)
```

## How it's built

All in `orderbook.py`:

- **Price levels:** `bids` and `asks` are dicts of `price -> deque of orders`.
  New orders go on the back of the deque and fills come off the front, so
  time priority comes for free.
- **Best price:** there's a heap of prices for each side so getting the best
  bid/ask is O(log n). Python's `heapq` is only a min heap, so bids are
  stored as negative numbers.
- **Cancelling:** `orders` is a dict from order id to the order, so a cancel
  is O(1). Taking an order out of the middle of a deque would be O(n), so
  instead it just gets marked as cancelled and is skipped when it reaches
  the front. Empty price levels get removed from the heap the same way.

## Testing

```
pytest
```

Besides some normal unit tests, `reference_book.py` is a deliberately dumb
version of the book that just loops over every resting order to find the best
match. The test generates 1,000 random sequences of 200 orders each (limit,
market and cancels mixed together, with prices in a tight range so lots of
them cross) and checks that both books produce exactly the same trade log.

## Things I noticed / might add

- The lazy cancel thing was the trickiest part. At first I didn't think about
  a price level where every order is cancelled, which still looks like the
  "best price" even though there's nothing there.
- The brute force comparison caught way more than the unit tests would have.
  If you break the time priority on purpose, it fails right away.
- Could add order modify (change qty/price), stop orders, or rewrite it in
  C++ with `std::map` to compare speed.
