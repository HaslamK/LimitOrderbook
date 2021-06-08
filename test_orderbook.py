from .orderbook import *

# To test:
# bids added
# best bid
# bids updated
# bids deleted
# asks added
# best ask
# asks updated
# asks deleted

# multi ticker bids + update


def test_case_a():
    # Dict/Hashmap to map orderID to ticker
    order_map = {}
    order_books = {}

    buy_orders = [
        "1568390243|abbb11|a|AAPL|B|209.00000|100",
        "1568390244|abbb11|u|101",
        "1568390245|abbb11|c"
    ]
    sell_orders = [
        "1568390243|abbb12|a|AAPL|S|209.00000|100",
        "1568390244|abbb12|u|101",
        "1568390245|abbb12|c"
    ]

    # test add/update/cancel buys and get_bid
    process_order(order_books, buy_orders[0], order_map)
    assert get_bid('AAPL', order_books) == 209.0
    process_order(order_books, buy_orders[1], order_map)
    assert order_books['AAPL'].get_mkt_depth(0)[1][0][1] == 101
    process_order(order_books, buy_orders[2], order_map)
    assert get_bid('AAPL', order_books) == -1

    # test add/update/cancel sells and get_ask
    process_order(order_books, sell_orders[0], order_map)
    assert get_ask('AAPL', order_books) == 209.0
    process_order(order_books, sell_orders[1], order_map)
    assert order_books['AAPL'].get_mkt_depth(0)[0][0][1] == 101
    process_order(order_books, sell_orders[2], order_map)
    assert get_ask('AAPL', order_books) == -1


def test_case_b():
    # Dict/Hashmap to map orderID to ticker
    order_map = {}
    order_books = {}

    orders = [
        "1568390201|abbb11|a|AAPL|B|209.00000|100",
        "1568390202|abbb12|a|AAPL|S|210.00000|10",
        "1568390204|abbb11|u|10",
        "1568390203|abbb12|u|101",
        "1568390243|abbb11|c",
        "1568390244|abbb12|c"
    ]

    # test orders
    process_order(order_books, orders[0], order_map)
    assert get_bid('AAPL', order_books) == 209.0
    assert order_books['AAPL'].get_mkt_depth(0)[1][0][1] == 100
    process_order(order_books, orders[1], order_map)
    assert get_ask('AAPL', order_books) == 210.0
    assert order_books['AAPL'].get_mkt_depth(0)[0][0][1] == 10

    # test updates
    process_order(order_books, orders[2], order_map)
    assert order_books['AAPL'].get_mkt_depth(0)[1][0][1] == 10
    process_order(order_books, orders[3], order_map)
    assert order_books['AAPL'].get_mkt_depth(0)[0][0][1] == 101

    # test cancels
    process_order(order_books, orders[4], order_map)
    assert len(order_books['AAPL'].get_mkt_depth(0)[1]) == 0
    process_order(order_books, orders[5], order_map)
    assert len(order_books['AAPL'].get_mkt_depth(0)[0]) == 0


def test_multiple_tickers():
    order_map = {}
    order_books = {}

    orders = [
        "1568390201|abbb11|a|AAPL|B|209.00000|100",
        "1568390202|abbb12|a|TSLA|S|1000.00000|10",
    ]

    process_order(order_books, orders[0], order_map)
    process_order(order_books, orders[1], order_map)
    assert get_bid('AAPL', order_books) == 209.0
    assert get_ask('TSLA', order_books) == 1000.0