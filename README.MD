# Order book simulation

requisites:
* bintrees
* pytest

To test:

In working dir, run "pytest"

Example use:

    order_map = {}
    order_books = {}

    order_a = "1568390243|abbb11|a|AAPL|B|209.00000|100"
    order_a2 = "1568390243|abbb12|a|AAPL|S|220.00000|10000"
    order_a3 = "1568390243|abbb13|a|AAPL|B|220.00000|10000"

    order_b = "1568390244|abbb11|u|101"
    order_c = "1568390245|abbb11|c"

    process_order(order_books, order_a, order_map)
    print(get_bid('AAPL', order_books))
    print(order_books['AAPL'].get_mkt_depth(0))
    process_order(order_books, order_a2, order_map)
    print(get_bind_and_ask('AAPL', order_books))
    print(order_books['AAPL'].get_mkt_depth(0))
    process_order(order_books, order_a3, order_map)
    print(order_books['AAPL'].get_mkt_depth(0))

Note: implemented as multiple books, one for each ticker & contained within order_books dict. 
Also requiring an ordermap dict for order:book lookups.