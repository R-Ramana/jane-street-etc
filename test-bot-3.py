#!/usr/bin/python

# ~~~~~==============   HOW TO RUN   ==============~~~~~
# 1) Configure things in CONFIGURATION section
# 2) Change permissions: chmod +x bot.py
# 3) Run in loop: while true; do ./bot.py; sleep 1; done

from __future__ import print_function

import sys
import socket
import json
from collections import deque

# ~~~~~============== CONFIGURATION  ==============~~~~~
# replace REPLACEME with your team name!
team_name = "NULLPOINTEREXCEPTION"
# This variable dictates whether or not the bot is connecting to the prod
# or test exchange. Be careful with this switch!
test_mode = True

# This setting changes which test exchange is connected to.
# 0 is prod-like
# 1 is slower
# 2 is empty
test_exchange_index = 1
prod_exchange_hostname = "production"

port = 25000 + (test_exchange_index if test_mode else 0)
exchange_hostname = "test-exch-" + \
    team_name if test_mode else prod_exchange_hostname

buy_orders = dict()
sell_orders = dict()
shares = dict()
shares['BOND'] = 0
shares['VALE'] = 0
shares['VALBZ'] = 0
counter = 0
best_prices = dict()
stockFairPrices = {"VALBZ": 0, "GS": 0, "MS": 0, "WFC": 0}

# ~~~~~============== NETWORKING CODE ==============~~~~~


def connect():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((exchange_hostname, port))
    return s.makefile('rw', 1)


def write_to_exchange(exchange, obj):
    json.dump(obj, exchange)
    exchange.write("\n")


def read_from_exchange(exchange):
    return json.loads(exchange.readline())

# ~~~~~============== MESSAGES CODE ==============~~~~~


def convert(counter, exchange, symbol, size, dir):
    counter += 1
    payload = {
        "type": "convert",
        "order_id": counter,
        "symbol": symbol,
        "dir": dir,
        "size": size
    }
    write_to_exchange(exchange, payload)

    return counter


def convert_to(shares, counter, exchange, symbol, size):
    shares[symbol] += size
    shares['VALBZ'] -= size
    return convert(counter, exchange, symbol, size, "BUY")


def convert_from(shares, counter, exchange, symbol, size):
    shares[symbol] -= size
    shares['VALBZ'] += size
    return convert(counter, exchange, symbol, size, "SELL")


def buy(buy_orders, counter, exchange, symbol, price, size):
    counter += 1

    payload = {
        "type": "add",
        "order_id": counter,
        "symbol": symbol,
        "dir": "BUY",
        "price": price,
        "size": size
    }

    buy_orders.append(counter)
    write_to_exchange(exchange, payload)

    return counter


def sell(sell_orders, counter, exchange, symbol, price, size):
    counter += 1

    payload = {
        "type": "add",
        "order_id": counter,
        "symbol": symbol,
        "dir": "SELL",
        "price": price,
        "size": size
    }

    sell_orders.append(counter)
    write_to_exchange(exchange, payload)

    return counter


def cancel(exchange, order_id):
    payload = {
        "type": "cancel",
        "order_id": order_id
    }
    write_to_exchange(exchange, payload)


def getStockFairPrice(bookMessage, stockFairPrices):

    symbol = bookMessage["symbol"]
    maxBuyPrice = bookMessage['buy'][0][0]
    minSellPrice = bookMessage['sell'][0][0]
    currentFairPrice = (maxBuyPrice + minSellPrice) / 2
    prevFairPrice = stockFairPrices[symbol]

    if (prevFairPrice > 0):

        fairPrice = (prevFairPrice + currentFairPrice) / 2
        return symbol, fairPrice

    return symbol, currentFairPrice


def getXLFFairPrice(stockFairPrices):
    return 0.3*1000 + 0.2*stockFairPrices["GS"] + 0.3*stockFairPrices["MS"] + 0.2*stockFairPrices["WFC"]


def getVALEFairPrice(stockFairPrices):
    return stockFairPrices["VALBZ"]


def sellHigherThanFairPrice(sell_orders, counter, exchange, symbol, message, shares):
    if len(message['buy']) > 0 and message['buy'][0][0] > 1000 and shares['BOND'] > 0:
        counter = sell(sell_orders, counter, exchange, 'BOND',
                       message['buy'][0][0], message['buy'][0][1])
        shares['BOND'] -= message['buy'][0][1] if shares["BOND"] >= message['buy'][0][1] else shares["BOND"]
        print(shares)


def cancelPastOrders(sell_orders):
    if len(sell_orders) > 0:
        sell_orders.popleft()

# ~~~~~============== MAIN LOOP ==============~~~~~


def add_to_market(message):
    symbol = message["symbol"]
    if (len(message['buy']) > 0):
        buy_price = message['buy'][0]
    elif symbol in best_prices:
        buy_price = best_prices[symbol][0]
    else:
        buy_price = (0, 0)

    if (len(message['buy']) > 0):
        sell_price = message['buy'][0]
    elif symbol in best_prices:
        sell_price = best_prices[symbol][1]
    else:
        sell_price = (0, 0)

    best_prices[symbol] = (buy_price, sell_price)


def check_xlf(counter, exchange, message):
    symbol = message["symbol"]

    if (symbol == "XLF"):
        xlf_buy_pricenum, xlf_sell_pricenum = best_prices["XLF"]
        xlfFairPrice = getXLFFairPrice(stockFairPrices)

        xlf_buy_price, xlf_buy_num = xlf_buy_pricenum
        xlf_sell_price, xlf_sell_num = xlf_sell_pricenum

        if(xlf_buy_price < xlfFairPrice):
            buy(buy_orders, counter, exchange, symbol, price, size)
        if(xlf_sell_price > xlfFairPrice):
            sell(buy_orders, counter, exchange, symbol, price, size)
    return


# ~~~~~============== MAIN LOOP ==============~~~~~


def main():
    exchange = connect()
    write_to_exchange(exchange, {"type": "hello", "team": team_name.upper()})
    hello_from_exchange = read_from_exchange(exchange)
    # A common mistake people make is to call write_to_exchange() > 1
    # time for every read_from_exchange() response.
    # Since many write messages generate marketdata, this will cause an
    # exponential explosion in pending messages. Please, don't do that!
    print("The exchange replied:", hello_from_exchange, file=sys.stderr)
    shares = dict()
    shares['BOND'] = 0
    shares['VALBZ'] = 0
    shares['VALE'] = 0
    counter = 0
    buy_orders = deque()
    sell_orders = deque()
    while True:
        message = read_from_exchange(exchange)
        if message['type'] == 'book':
            add_to_market(message)
            print(best_prices)
            if message['symbol'] == 'BOND':
                print(message)

        elif message['type'] == 'trade':
            continue
        else:
            print(message)
            continue
        if message['type'] == 'book':
            if message['symbol'] == 'BOND':
                if len(message['buy']) > 0 and message['buy'][0][0] > 1000 and shares['BOND'] > 0:
                    counter = sell(sell_orders, counter, exchange, 'BOND',
                                   message['buy'][0][0], message['buy'][0][1])
                    shares['BOND'] -= message['buy'][0][1] if shares["BOND"] >= message['buy'][0][1] else shares["BOND"]
                    print(shares)
                if len(message['sell']) > 0 and message['sell'][0][0] <= 1000:
                    counter = buy(buy_orders, counter, exchange, 'BOND',
                                  message['sell'][0][0], message['sell'][0][1])
                    shares['BOND'] += message['sell'][0][1]
                    print(shares)
            if message['symbol'] == 'VALE' or message['symbol'] == 'VALBZ':
                if shares['VALBZ'] == 0:
                    if message['symbol'] == 'VALBZ':
                        counter = buy(buy_orders, counter, exchange, 'VALBZ',
                                      message['sell'][0][0], message['sell'][0][1])
                        shares['VALBZ'] += message['sell'][0][1]
                # if 'VALE' in shares:
                #     print (shares)
                #     counter = convert_from(shares, counter, exchange, 'VALE', 1)
                # elif 'VALBZ' in shares:
                #     print (shares)
                #     counter = convert_to(shares, counter, exchange, 'VALE', 1)

        if(message["type"] == "close"):
            print("The round has ended")
            break


if __name__ == "__main__":
    main()
