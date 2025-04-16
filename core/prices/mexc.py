# ------------------------------------------
# Файл: mexc.py (core/prices)
# Назначение: Асинхронная загрузка цен с биржи MEXC через библиотеку CCXT.
# Скрипт фильтрует только активные торговые пары к USDT на спотовом рынке,
# получает последние данные (last, ask, bid) и сохраняет их в JSON-файл.
# ------------------------------------------

import json  # модуль для сохранения данных в формате JSON
import ccxt.async_support as ccxt  # асинхронная версия библиотеки CCXT

# Асинхронная функция получения цен с биржи MEXC
async def mexc_price():
    # Инициализируем подключение к бирже MEXC с включенным ограничением частоты запросов
    exchange = ccxt.mexc({
        'enableRateLimit': True,
    })
    
    try:
        # Загружаем все доступные торговые рынки с биржи
        markets = await exchange.load_markets()

        pairs = []  # список подходящих торговых пар
        for symbol, market in markets.items():
            if not isinstance(symbol, str):
                continue  # пропускаем некорректные ключи
            if '/USDT' not in symbol:
                continue  # оставляем только пары к USDT
            if not market.get('spot', False):
                continue  # фильтруем только спотовые пары
            pairs.append(symbol)

        # Если не найдено ни одной подходящей пары — выводим ошибку
        if not pairs:
            print("[ERROR][MEXC] No valid trading pairs found. Check filtering logic.")

        # Загружаем тикеры для всех выбранных пар
        try:
            tickers = await exchange.fetch_tickers(pairs)
        except Exception as e:
            print(f"[ERROR][MEXC] fetch_tickers failed: {e}")
            return

        data = {}  # финальный словарь с ценами
        for symbol, ticker in tickers.items():
            try:
                data[symbol] = {
                    'last': float(ticker['last']),  # последняя цена сделки
                    'ask': float(ticker['ask']),    # цена продажи
                    'bid': float(ticker['bid']),    # цена покупки
                }
            except Exception as e:
                continue  # пропускаем, если данные невалидны

        # Создаем папку для сохранения, если она не существует
        import os
        os.makedirs("data/price", exist_ok=True)

        # Сохраняем результат в JSON-файл
        with open('data/price/mexc_price.json', 'w') as f:
            json.dump(data, f)
            
    except Exception as e:
        # Общая ошибка при выполнении
        print('Error mexc occurred:', e)
        
    finally:
        # Закрываем подключение к бирже
        await exchange.close()