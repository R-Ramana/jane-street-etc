#!/usr/bin/python

# ~~~~~==============   HOW TO RUN   ==============~~~~~
# 1) Configure things in CONFIGURATION section
# 2) Change permissions: chmod +x bot.py
# 3) Run in loop: while true; do ./bot.py; sleep 1; done

from __future__ import print_function

import sys
import socket
import json
import uuid
import collections

# ~~~~~============== CONFIGURATION  ==============~~~~~
# replace REPLACEME with your team name!
team_name="NULLPOINTEREXCEPTION"
# This variable dictates whether or not the bot is connecting to the prod
# or test exchange. Be careful with this switch!
test_mode = False

# This setting changes which test exchange is connected to.
# 0 is prod-like
# 1 is slower
# 2 is empty
test_exchange_index=1
prod_exchange_hostname="production"

port=25000 + (test_exchange_index if test_mode else 0)
exchange_hostname = "test-exch-" + team_name if test_mode else prod_exchange_hostname

buy_orders = dict()
sell_orders = dict()
shares = dict()
shares['BOND'] = 0
counter = 0

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
def convert(exchange, symbol, size, dir):
    payload = {
        "type": "convert",
        "order_id" : str(uuid.uuid4()),
        "symbol": symbol,
        "dir" : dir,
        "size" : size
    }
    write_to_exchange(exchange, payload)

def convert_to(exchange, symbol, size):
    convert(exchange, symbol, size, "BUY")

def convert_from(exchange, symbol, size):
    convert(exchange, symbol, size, "SELL")
    
def buy(counter, exchange, symbol, price, size):
    counter += 1
    
    payload = {
        "type": "add",
        "order_id": counter,
        "symbol": symbol,
        "dir": "BUY",
        "price": price,
        "size": size
        }

    buy_orders[symbol] = [price, size, counter]
    write_to_exchange(exchange, payload)

def sell(counter, exchange, symbol, price, size):
    counter += 1
    
    payload = {
        "type": "add",
        "order_id": counter,
        "symbol": symbol,
        "dir": "SELL",
        "price": price,
        "size": size
        }
    
    sell_orders[symbol] = [price, size, counter]
    write_to_exchange(exchange, payload)

def cancel(exchange, order_id):
    payload = {
        "type" : "cancel",
        "order_id" : order_id
    }
    write_to_exchange(exchange, payload)

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
    while True:
        
        message = read_from_exchange(exchange)
        if message['type'] == 'book' or message['type'] == 'trade':
            if message['symbol'] == 'BOND': print(message)
        else: print(message)
        if message['type'] == 'book':
            if message['symbol'] == 'BOND':
                if len(message['buy']) > 0 and message['buy'][0][0] > 1000 and shares['BOND'] > 0:
                    sell(counter, exchange, 'BOND', message['buy'][0][0], message['buy'][0][1])
                    shares['BOND'] -= message['buy'][0][1] if shares["BOND"] >= message['buy'][0][1] else shares["BOND"]
                    print(shares)
                if len(message['sell']) > 0 and message['sell'][0][0] <= 1000:
                    buy(counter, exchange, 'BOND', message['sell'][0][0], message['sell'][0][1])
                    if read_from_exchange(exchange)['type'] == 'ack':
                    print(shares)

        if(message["type"] == "close"):
            print("The round has ended")
            break

if __name__ == "__main__":
    main()
