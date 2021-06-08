from bintrees import FastAVLTree
# todo ticker map to inside order book??


class OrderBook:
    def __init__(self):
        # AVL trees are used as a main structure due its optimal performance features for this purpose

        self._asks = FastAVLTree()  # MIN Heap
        self._bids = FastAVLTree()  # MAX Heap
        self._price_ids = FastAVLTree()  # Assigning ID -> Price

        self._total_ask_size = 0  # For monitoring purpose
        self._total_bid_size = 0  # For monitoring purpose

        # self._last_order_id = 0  # Increases with each order processed
        self._cleared_orders_count = 0  # For monitoring purpose
        self._total_volume_traded = 0  # For monitoring purpose
        self._total_volume_pending = 0  # For monitoring purpose

    def _balance(self, trades_stack):
        """ Executes trades if it finds liquidity for them """

        # No liquidity at all
        if self._asks.is_empty() or self._bids.is_empty():
            return trades_stack

        min_ask = self._asks.min_key()
        max_bid = self._bids.max_key()

        # Check liquidity situation
        if max_bid >= min_ask:
            ask_orders = self._asks.get(min_ask)
            bid_orders = self._bids.get(max_bid)

            for ask_order in ask_orders:
                for bid_order in bid_orders:
                    if not ask_order in ask_orders or not bid_order in bid_orders:
                        continue

                    traded = min(ask_orders[ask_order], bid_orders[bid_order])

                    ask_orders[ask_order] -= traded
                    bid_orders[bid_order] -= traded

                    self._total_ask_size -= traded
                    self._total_bid_size -= traded

                    self._total_volume_traded += traded
                    self._total_volume_pending -= 2 * traded

                    # Buy side order fully liquidated
                    if bid_orders[bid_order] == 0:
                        # print("BID ORDER LIQUIDATED")
                        self._cleared_orders_count += 1
                        del bid_orders[bid_order]
                        del self._price_ids[bid_order]

                    # Sell side order fully liquidated
                    if ask_orders[ask_order] == 0:
                        # print("ASK ORDER LIQUIDATED")
                        self._cleared_orders_count += 1
                        del ask_orders[ask_order]
                        del self._price_ids[ask_order]

                    # Inform sides about state of their orders
                    trades_stack.append((0, traded, max_bid))
                    trades_stack.append((1, ask_order, traded, max_bid, 'ask'))
                    trades_stack.append((1, bid_order, traded, max_bid, 'bid'))

            # Whole ASK price level were liquidated, remove it from three and let it rebalance
            if self._asks[min_ask].is_empty():
                # print("ASK level liquidated")
                del self._asks[min_ask]

            # Whole BID price level were liquidated, remove it from three and let it rebalance
            if self._bids[max_bid].is_empty():
                # print("BID level liquidated")
                del self._bids[max_bid]
        else:
            return trades_stack

        return self._balance(trades_stack)

    @property
    def ask(self):
        """ Best ask """

        try:
            return self.get_mkt_depth(1)[0][0][0]
        except:
            return -1

    @property
    def bid(self):
        """ Best bid """

        try:
            return self.get_mkt_depth(1)[1][0][0]
        except:
            return -1

    def _submit_lmt(self, side, size, price, order_id):
        """ Submits LMT order to book """

        # Assign order ID
        order_id = order_id  # redundant...

        # Pending volume monitoring
        self._total_volume_pending += size
        self._price_ids.insert(order_id, (price, side))

        # Assign to right (correct) side
        if side == 'S':  # ask
            self._total_ask_size += size
            ask_level = self._asks.get(price, FastAVLTree())
            ask_level.insert(order_id, size)

            if price not in self._asks:
                self._asks.insert(price, ask_level)
        else:  # bid
            self._total_bid_size += size
            bid_level = self._bids.get(price, FastAVLTree())
            bid_level.insert(order_id, size)

            if price not in self._bids:
                self._bids.insert(price, bid_level)

        return order_id

    def _cancel(self, order_id):
        """ Cancel order """

        # Finds and cancels order

        order = self._price_ids[order_id]

        if order[1] == 'S':
            del self._asks[order[0]][order_id]

            if self._asks[order[0]].is_empty():
                del self._asks[order[0]]
        else:
            del self._bids[order[0]][order_id]

            if self._bids[order[0]].is_empty():
                del self._bids[order[0]]

    def _update(self, order_id, size):
        order = self._price_ids[order_id]

        if order[1] == 'S':
            self._asks[order[0]][order_id] = size

        else:
            # print(self._bids[order[0]][order_id])
            self._bids[order[0]][order_id] = size

    def submit_order(self, order):
        """ Abstraction on order action """

        if order.action == 'a':
            order_id = self._submit_lmt(order.side, order.size, order.price, order.id)
            trades = self._balance([])
            return order_id, trades

        if order.action == 'c':
            self._cancel(order.id)

        if order.action == 'u':
            self._update(order.id, order.size)

    def get_mkt_depth(self, depth):
        """ Liquidity levels size for both bid and ask """

        ask_side = []
        if not self._asks.is_empty():
            for price in self._asks.keys():
                ask_level = self._asks.get(price)
                ask_size = 0
                for order_id in ask_level.keys():
                    # print(ask_size, order_id, ask_level.get(order_id))
                    ask_size += ask_level.get(order_id)

                ask_side.append([price, ask_size])

                if len(ask_side) >= depth:
                    break

        bid_side = []
        if not self._bids.is_empty():
            for price in self._bids.keys(reverse=True):
                bid_level = self._bids.get(price)
                bid_size = 0
                for order_id in bid_level.keys():
                    bid_size += bid_level.get(order_id)

                bid_side.append([price, bid_size])

                if len(bid_side) >= depth:
                    break

        return [ask_side, bid_side]


class Order:
    order_str = None

    timestamp = None
    id = None
    action = None
    ticker = None  # todo if diff ticker make new book?
    side = None
    price = None
    size = None

    def __init__(self, order_str):
        self._parse_order(order_str)

    def __repr__(self):
        return self.order_str

    def _parse_order(self, order_str):
        if type(order_str) != str:
            return
        order_str = order_str.strip()
        order_ls = order_str.split('|')
        # print(order_ls)
        self.order_str = order_str
        if len(order_ls) == 1:
            return

        self.timestamp = order_ls[0]
        self.id = order_ls[1]
        self.action = order_ls[2]

        if order_ls[2] == 'a':
            self.ticker = order_ls[3]
            self.side = order_ls[4]
            self.price = float(order_ls[5])
            self.size = int(order_ls[6])
        elif order_ls[2] == 'u':
            self.size = int(order_ls[3])
        elif order_ls[2] == 'c':
            pass
        return


def process_order(order_books, order, order_map):
    # todo error handling around messages and orders
    # Not all orders have a ticker!!!
    order = Order(order)
    if order.price == 0:
        print("Invalid price 0, order not submitted")
        return

    order_id = order.id
    if order.action == 'a':
        ticker = order.ticker

        if ticker not in order_books:
            order_books[ticker] = OrderBook()

        order_books[ticker].submit_order(order)
        order_map[order_id] = ticker

    elif order.action in ['u', 'c']:
        ticker = order_map.get(order_id)
        order_books[ticker].submit_order(order)

    # return order_books


def get_bid(ticker, books):
    return books[ticker].bid


def get_ask(ticker, books):
    return books[ticker].ask


def get_bind_and_ask(ticker, books):
    bid = get_bid(ticker, books)
    ask = get_ask(ticker, books)
    return f"bid: {bid}  -  ask: {ask}"


if __name__ == '__main__':
    # Dict/Hashmap to map orderID to ticker
    order_map = {}
    order_books = {}

    order_a = "1568390243|abbb11|a|AAPL|B|209.00000|100"
    order_a2 = "1568390244|abbb12|a|AAPL|B|220.00000|20000"
    order_a3 = "1568390245|abbb13|a|AAPL|B|220.00000|10000"

    order_b = "1568390244|abbb11|u|101"
    order_c = "1568390245|abbb11|c"

    process_order(order_books, order_a, order_map)
    print(get_bid('AAPL', order_books))
    print(order_books['AAPL'].get_mkt_depth(0))
    process_order(order_books, order_a2, order_map)
    process_order(order_books, order_a3, order_map)

    # print(order_books['AAPL']._price_ids)
    print(order_books['AAPL']._bids)
    print(order_books['AAPL']._asks)
    print(get_bind_and_ask('AAPL', order_books))
    print(order_books['AAPL'].get_mkt_depth(0))
    print(order_books['AAPL'].get_mkt_depth(0))

    print(get_bid('AAPL', order_books))
    process_order(order_books, order_b, order_map)
    print(get_bid('AAPL', order_books))
    process_order(order_books, order_c, order_map)
    print(get_bid('AAPL', order_books))

