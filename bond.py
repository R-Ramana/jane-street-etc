from exchange import sell, buy

def sellBondHigherThanFairPrice(sell_orders, counter, exchange, message, shares):
    if len(message['buy']) > 0 and message['buy'][0][0] > 1000 and shares['BOND'] > -100:
        counter = sell(sell_orders, counter, exchange, 'BOND', message['buy'][0][0], message['buy'][0][1])
        shares['BOND'] -= message['buy'][0][1]
        print(shares)

def buyBondLowerThanFairPrice(buy_orders, counter, exchange, message, shares):
    if len(message['sell']) > 0 and message['sell'][0][0] < 1000 and shares['BOND'] < 100:
        counter = buy(buy_orders, counter, exchange, 'BOND', message['sell'][0][0], message['sell'][0][1])
        shares['BOND'] += message['sell'][0][1]
        print(shares)