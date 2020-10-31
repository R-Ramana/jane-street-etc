def sellStockHigherThanFairPrice(sell_orders, counter, exchange, message, shares):
    
    symbol = message['symbol']
    fairPrice = getAndUpdateStockFairPrice(message, stockFairPrices)

    if len(message['buy']) > 0 and message['buy'][0][0] > fairPrice and shares[symbol] > 0:
        counter = sell(sell_orders, counter, exchange, symbol, message['buy'][0][0], message['buy'][0][1])
        shares[symbol] -= message['buy'][0][1] if shares[symbol] >= message['buy'][0][1] else shares[symbol]
        print(shares)
        print("SOMETHING SOLD!")

def buyStockLowerThanFairPrice(buy_orders, counter, exchange, message, shares):

    symbol = message['symbol']
    fairPrice = getAndUpdateStockFairPrice(message, stockFairPrices)

    if len(message['sell']) > 0 and message['sell'][0][0] <= fairPrice:
        counter = buy(buy_orders, counter, exchange, symbol, message['sell'][0][0], message['sell'][0][1])
        shares[symbol] += message['sell'][0][1]
        print(shares)
        print("SOMETHING BOUGHT!")

def getAndUpdateStockFairPrice(bookMessage, stockFairPrices):
    
    symbol = bookMessage["symbol"]
    maxBuyPrice = bookMessage['buy'][0][0]
    minSellPrice = bookMessage['sell'][0][0]
    currentFairPrice = (maxBuyPrice + minSellPrice) / 2
    prevFairPrice = stockFairPrices[symbol]

    if (prevFairPrice > 0):
        fairPrice = prevFairPrice * 0.9 + currentFairPrice * 0.1
        stockFairPrices[symbol] = fairPrice
        return prevFairPrice
    stockFairPrices[symbol] = currentFairPrice
    return currentFairPrice