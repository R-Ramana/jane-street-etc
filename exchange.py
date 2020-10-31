from networking import write_to_exchange

def convert(counter, exchange, symbol, size, dir):
    payload = {
        "type": "convert",
        "order_id" : counter,
        "symbol": symbol,
        "dir" : dir,
        "size" : size
    }
    write_to_exchange(exchange, payload)

    return counter

def convert_to(counter, exchange, symbol, size):
    return convert(counter, exchange, symbol, size, "BUY")

def convert_from(counter, exchange, symbol, size):
    return convert(counter, exchange, symbol, size, "SELL")

def add(buy_orders, counter, exchange, symbol, price, size, dir):
    counter += 1
    
    payload = {
        "type": "add",
        "order_id": counter,
        "symbol": symbol,
        "dir": dir,
        "price": price,
        "size": size
        }

    write_to_exchange(exchange, payload)

    return counter

def buy(buy_orders, counter, exchange, symbol, price, size):
    counter = add(buy_orders, counter, exchange, symbol, price, size, "BUY")
    buy_orders.append(counter)
    return counter

def sell(sell_orders, counter, exchange, symbol, price, size):
    counter = add(sell_orders, counter, exchange, symbol, price, size, "SELL")
    sell_orders.append(counter)
    return counter

def cancel(exchange, order_id):
    payload = {
        "type" : "cancel",
        "order_id" : order_id
    }
    write_to_exchange(exchange, payload)