import json
import ccxt.async_support as ccxt


async def okex_price():
    # Создаем объект OKEx
    exchange = ccxt.okex()

    # Получаем список всех пар торгующихся на бирже OKEx
    markets = await exchange.load_markets()

    # Создаем список пар, торгующихся с USDT
    usdt_markets = [market for market in markets if '/USDT' in market and markets[market]['spot'] and markets[market]['active']]
    
    # Получаем информацию о последней цене, цене продажи и цене покупки для всех выбранных пар
    tickers = await exchange.fetch_tickers(usdt_markets)

    # Создаем словарь для хранения информации о парах
    pairs_info = {}

    # Заполняем словарь информацией о каждой паре
    for market in tickers:
        ticker = tickers[market]
        last_price = ticker['last']
        ask_price = ticker['ask']
        bid_price = ticker['bid']
        pairs_info[market] = {"last": last_price, "ask": ask_price, "bid": bid_price}

    # Сохраняем словарь в файле JSON
    import os; os.makedirs("data/price", exist_ok=True)
    with open("data/price/okex_price.json", "w") as f:
        json.dump(pairs_info, f)

    await exchange.close()
