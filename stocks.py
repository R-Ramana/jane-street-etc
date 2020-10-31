from exchange import sell, buy

def sellStockHigherThanFairPrice(sell_orders, counter, exchange, message, shares, stockFairPrices):
    
    symbol = str(message['symbol'])

    if len(message['buy']) > 0 and shares[symbol] > -100:

        fairPrice = getAndUpdateStockFairPrice(message, stockFairPrices)
        if message['buy'][0][0] > fairPrice and fairPrice > 0:
            maxSell = abs(-100 - shares[symbol])
            size = message['sell'][0][1] if maxSell < message['sell'][0][1] else maxSell
            counter = sell(sell_orders, counter, exchange, symbol, message['buy'][0][0], size)
            shares[symbol] -= size
            print(shares)
            print("SOMETHING SOLD!")
    
    return counter

def buyStockLowerThanFairPrice(buy_orders, counter, exchange, message, shares, stockFairPrices):

    symbol = str(message['symbol'])

    if len(message['sell']) > 0 and shares[symbol] < 100:

        fairPrice = getAndUpdateStockFairPrice(message, stockFairPrices)
        if message['sell'][0][0] < fairPrice:
            maxBuy = 100 - shares[symbol]
            size = message['sell'][0][1] if maxBuy < message['sell'][0][1] else maxBuy
            counter = buy(buy_orders, counter, exchange, symbol, message['sell'][0][0], size)
            shares[symbol] += size
            print(shares)
            print("SOMETHING BOUGHT!")

    return counter

def getAndUpdateStockFairPrice(bookMessage, stockFairPrices):

    symbol = bookMessage["symbol"]
    if len(bookMessage['buy']) > 0 and len(bookMessage['sell']) > 0:
        maxBuyPrice = bookMessage['buy'][0][0]
        minSellPrice = bookMessage['sell'][0][0]
        currentFairPrice = int(maxBuyPrice*0.4 + minSellPrice*0.6)
        prevFairPrice = stockFairPrices[symbol]

        if (prevFairPrice > 0):
            fairPrice = int(prevFairPrice * 0.7 + currentFairPrice * 0.3)
            stockFairPrices[symbol] = fairPrice
            return prevFairPrice
        stockFairPrices[symbol] = currentFairPrice
        return currentFairPrice

    return stockFairPrices[symbol]