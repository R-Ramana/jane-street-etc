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
team_name="NULLPOINTEREXCEPTION"
# This variable dictates whether or not the bot is connecting to the prod
# or test exchange. Be careful with this switch!
test_mode = True

# This setting changes which test exchange is connected to.
# 0 is prod-like
# 1 is slower
# 2 is empty
test_exchange_index=0
prod_exchange_hostname="production"

port=25000 + (test_exchange_index if test_mode else 0)
exchange_hostname = "test-exch-" + team_name if test_mode else prod_exchange_hostname

stockFairPrices = {"VALBZ" : 0, "GS": 0, "MS": 0, "WFC": 0}

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
        "type" : "cancel",
        "order_id" : order_id
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
        counter = sell(sell_orders, counter, exchange, 'BOND', message['buy'][0][0], message['buy'][0][1])
        shares['BOND'] -= message['buy'][0][1] if shares["BOND"] >= message['buy'][0][1] else shares["BOND"]
        print(shares)

def cancelPastOrders(exchange, sell_orders, buy_orders, i):
    if i > 5:
        if len(sell_orders) > 0: 
            cancel(exchange, sell_orders.popleft())
        if len(buy_orders) > 0: 
            cancel(exchange, buy_orders.popleft())
        return 0

    else: return i

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
    counter = 0
    buy_orders = deque()
    sell_orders = deque()
    i = 0
    while True:
        i = cancelPastOrders(exchange, sell_orders, buy_orders, i)
        message = read_from_exchange(exchange)
        if(message["type"] == "close"):
            print("The round has ended")
            break
        if message['type'] == 'book':
            if message['symbol'] == 'BOND': print(message)
        elif message['type'] == 'trade': continue
        else:
            print(message)
            continue
        if message['type'] == 'book':
            if message['symbol'] == 'BOND':
                if len(message['buy']) > 0 and message['buy'][0][0] > 1000 and shares['BOND'] > 0:
                    counter = sell(sell_orders, counter, exchange, 'BOND', message['buy'][0][0], message['buy'][0][1])
                    shares['BOND'] -= message['buy'][0][1] if shares["BOND"] >= message['buy'][0][1] else shares["BOND"]
                    print(shares)
                if len(message['sell']) > 0 and message['sell'][0][0] <= 1000:
                    counter = buy(buy_orders, counter, exchange, 'BOND', message['sell'][0][0], message['sell'][0][1])
                    shares['BOND'] += message['sell'][0][1]
                    print(shares)

        

if __name__ == "__main__":
    main()
