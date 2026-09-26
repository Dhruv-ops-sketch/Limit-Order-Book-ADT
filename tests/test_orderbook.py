import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from orderbook import OrderBook
from reference_book import ReferenceBook

NUM_SEQUENCES = 1000
OPS_PER_SEQUENCE = 200


def test_no_match_when_prices_dont_cross():
    book = OrderBook()
    book.submit(1, "buy", 10, 99)
    book.submit(2, "sell", 10, 101)
    assert book.trades == []
    assert book.best_bid() == 99
    assert book.best_ask() == 101


def test_price_time_priority():
    book = OrderBook()
    book.submit(1, "sell", 5, 101)
    book.submit(2, "sell", 5, 100)
    book.submit(3, "sell", 5, 100)   # same price as 2 but later
    book.submit(4, "buy", 7, 101)
    # best price first (order 2), then order 3 since it came next
    assert book.trades == [(4, 2, 100, 5), (4, 3, 100, 2)]


def test_partial_fill_rests_leftover():
    book = OrderBook()
    book.submit(1, "sell", 5, 100)
    book.submit(2, "buy", 8, 100)
    assert book.trades == [(2, 1, 100, 5)]
    assert book.best_bid() == 100
    assert book.orders[2].qty == 3


def test_market_order_doesnt_rest():
    book = OrderBook()
    book.submit(1, "sell", 5, 100)
    book.submit(2, "buy", 10)
    assert book.trades == [(2, 1, 100, 5)]
    assert book.best_bid() is None
    assert 2 not in book.orders


def test_cancel():
    book = OrderBook()
    book.submit(1, "sell", 5, 100)
    book.submit(2, "sell", 5, 101)
    assert book.cancel(1)
    assert not book.cancel(1)        # already gone
    assert book.best_ask() == 101
    book.submit(3, "buy", 5, 101)
    assert book.trades == [(3, 2, 101, 5)]


def random_ops(rng, n):
    ops = []
    ids = []
    for i in range(1, n + 1):
        r = rng.random()
        if r < 0.15 and ids:
            ops.append(("cancel", rng.choice(ids)))
        else:
            side = rng.choice(["buy", "sell"])
            qty = rng.randint(1, 20)
            # small price range so orders actually cross a lot
            price = None if r < 0.25 else rng.randint(95, 105)
            ops.append(("order", i, side, qty, price))
            ids.append(i)
    return ops


def test_matches_reference():
    rng = random.Random(42)
    for _ in range(NUM_SEQUENCES):
        book = OrderBook()
        ref = ReferenceBook()
        for op in random_ops(rng, OPS_PER_SEQUENCE):
            if op[0] == "cancel":
                assert book.cancel(op[1]) == ref.cancel(op[1])
            else:
                _, order_id, side, qty, price = op
                book.submit(order_id, side, qty, price)
                ref.submit(order_id, side, qty, price)
        assert book.trades == ref.trades
