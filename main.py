from orderbook import OrderBook

# small demo so you can see what the book does

book = OrderBook()

book.submit(1, "sell", 10, 101)
book.submit(2, "sell", 5, 102)
book.submit(3, "sell", 8, 101)    # same price as order 1 but came later
book.submit(4, "buy", 7, 99)
book.submit(5, "buy", 3, 100)

print("starting book:")
book.show()

print("\nbuy 12 @ 101 (should take all of order 1 and 2 from order 3)")
book.submit(6, "buy", 12, 101)

print("\nmarket sell 5 (hits the best bids)")
book.submit(7, "sell", 5)

print("\ncancel order 2")
book.cancel(2)

print("\ntrades:")
for buy_id, sell_id, price, qty in book.trades:
    print(f"  buy #{buy_id} / sell #{sell_id}: {qty} @ {price}")

print("\nending book:")
book.show()
