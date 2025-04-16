# ------------------------------------------
# Файл: huobi.py (core/prices)
# Назначение: Получение цен всех активных USDT-пар с биржи Huobi через CCXT (асинхронно).
# Фильтруются только активные спотовые пары, и сохраняются данные о последней цене,
# лучшем спросе (bid) и лучшем предложении (ask) в JSON-файл.
# ------------------------------------------

import json  # модуль для работы с форматом JSON
import ccxt.async_support as ccxt  # асинхронная версия CCXT для подключения к биржам

# Асинхронная функция получения цен с биржи Huobi
async def huobi_price():
    # Инициализация биржи Huobi с включённым ограничением скорости запросов
    exchange = ccxt.huobi({
        'enableRateLimit': True,
    })
    
    try:
        # Загружаем список всех рынков на бирже Huobi
        markets = await exchange.load_markets()

        # Фильтруем: оставляем только активные торговые пары к USDT на спотовом рынке
        pairs = [
            symbol for symbol in markets
            if '/USDT' in symbol and markets[symbol]['spot'] and markets[symbol]['active']
        ]
        
        # Получаем тикеры (цену, bid, ask) для отфильтрованных пар
        tickers = await exchange.fetch_tickers(pairs)
        
        data = {}  # словарь для хранения результатов

        # Заполняем словарь данными по каждой паре
        for symbol, ticker in tickers.items():
            data[symbol] = {
                'last': ticker['last'],  # последняя цена сделки
                'ask': ticker['ask'],    # цена, по которой можно купить
                'bid': ticker['bid'],    # цена, по которой можно продать
            }
        
        # Создаём директорию, если она не существует
        import os
        os.makedirs("data/price", exist_ok=True)

        # Сохраняем словарь в JSON-файл
        with open('data/price/huobi_price.json', 'w') as f:
            json.dump(data, f)
            
    except Exception as e:
        # Обработка исключений — выводим сообщение об ошибке
        print('Error huobi occurred:', e)
        
    finally:
        # Закрываем соединение с биржей
        await exchange.close()