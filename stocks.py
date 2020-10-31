from exchange import sell, buy

def sellStockHigherThanFairPrice(sell_orders, counter, exchange, message, shares, stockFairPrices):
    
    symbol = message['symbol']

    if len(message['buy']) > 0 and shares[symbol] > -100:

        fairPrice = getAndUpdateStockFairPrice(message, stockFairPrices)
        if message['buy'][0][0] > fairPrice:
            counter = sell(sell_orders, counter, exchange, symbol, message['buy'][0][0], message['buy'][0][1])
            shares[symbol] -= message['buy'][0][1] if shares[symbol] >= message['buy'][0][1] else shares[symbol]
            print(shares)
            print("SOMETHING SOLD!")
    
    return counter

def buyStockLowerThanFairPrice(buy_orders, counter, exchange, message, shares, stockFairPrices):

    symbol = message['symbol']

    if len(message['sell']) > 0 and shares[symbol] < 100:

        fairPrice = getAndUpdateStockFairPrice(message, stockFairPrices)
        if message['sell'][0][0] < fairPrice:
            counter = buy(buy_orders, counter, exchange, symbol, message['sell'][0][0], message['sell'][0][1])
            shares[symbol] += message['sell'][0][1]
            print(shares)
            print("SOMETHING BOUGHT!")

    return counter

def getAndUpdateStockFairPrice(bookMessage, stockFairPrices):
    symbol = bookMessage["symbol"]
    
    if len(bookMessage['buy']) > 0 and len(bookMessage['sell']) > 0:
        maxBuyPrice = bookMessage['buy'][0][0]
        minSellPrice = bookMessage['sell'][0][0]
        currentFairPrice = (maxBuyPrice + minSellPrice) // 2
        prevFairPrice = stockFairPrices[symbol]

        if (prevFairPrice > 0):
            fairPrice = int(prevFairPrice * 0.9 + currentFairPrice * 0.1)
            stockFairPrices[symbol] = fairPrice
            return prevFairPrice
        stockFairPrices[symbol] = currentFairPrice
        return currentFairPrice

    return stockFairPrices[symbol]