# ------------------------------------------
# Файл: bybit.py (core/prices)
# Назначение: Асинхронная функция получения цен с биржи Bybit через API.
# Загружает все активные спотовые пары, торгуемые к USDT, и сохраняет
# данные по последней цене, цене покупки (bid) и продажи (ask) в JSON-файл.
# ------------------------------------------
import json  # для сохранения результата в файл JSON
import ccxt.async_support as ccxt  # асинхронный модуль для работы с крипто-биржами


# Асинхронная функция получения цен с биржи Bybit
async def bybit_price():
    # Инициализация подключения к бирже Bybit с ограничением частоты запросов (rate limit)
    exchange = ccxt.bybit({
        'enableRateLimit': True,
    })
    
    try:
        # Загружаем список всех торговых рынков биржи
        markets = await exchange.load_markets()

        # Фильтруем только активные пары типа SPOT, торгуемые к USDT
        pairs = [
            symbol for symbol in markets
            if '/USDT' in symbol and markets[symbol]['spot'] and markets[symbol]['active']
        ]

        # Получаем тикеры по всем отфильтрованным парам (асинхронно)
        tickers = await exchange.fetch_tickers(pairs)
        
        # Словарь для хранения отформатированных данных
        data = {}
        for symbol, ticker in tickers.items():
            # Сохраняем последние данные по каждой паре: цена, bid, ask
            data[symbol] = {
                'last': ticker['last'],  # последняя цена сделки
                'ask': ticker['ask'],    # лучшая цена продажи
                'bid': ticker['bid'],    # лучшая цена покупки
            }
        
        # Создаём директорию, если она не существует
        import os
        os.makedirs("data/price", exist_ok=True)

        # Сохраняем результат в файл JSON
        with open('data/price/bybit_price.json', 'w') as f:
            json.dump(data, f)
            
    except Exception as e:
        # Обработка ошибок — вывод в консоль
        print('Error Bybit occurred:', e)
        
    finally:
        # Закрываем соединение с биржей
        await exchange.close()