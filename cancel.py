from exchange import cancel

def cancelPastOrders(exchange, sell_orders, buy_orders, i):
    if i == 5:
        if len(sell_orders) > 0: 
            cancel(exchange, sell_orders.popleft())
        if len(buy_orders) > 0: 
            cancel(exchange, buy_orders.popleft())
        return 0