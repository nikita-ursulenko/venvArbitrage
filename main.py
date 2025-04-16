# ------------------------------------------
# Файл: main.py
# Назначение: Главный асинхронный скрипт, который запускается для получения цен с бирж,
# расчёта арбитражных спредов, обновления комиссий и формирования результирующего JSON.
# Основные этапы:
# 1. Загрузка всех цен через fetch_all_prices().
# 2. Поиск минимального ask и максимального bid.
# 3. Расчёт спредов между биржами.
# 4. Загрузка комиссий с бирж OKEX, Gateio, Huobi и MEXC.
# 5. Обновление данных с учётом комиссий и фильтрация неподходящих монет.
# 6. Сохранение результата в data/main.json
# ------------------------------------------

import asyncio
import json
import os

import ccxt.async_support as ccxt
from web3 import Web3, HTTPProvider

from config.ccxt_init import okex, gateio, huobi, mexc
from core.fees.utils import fetch_fees
from core.cleaner import delete_keys
from core.prices import fetch_all_prices
from core.spread import calculate_spread, find_max_bid, find_min_ask
from core.updater import update_fees



async def main():
    # Получаем актуальные цены всех поддерживаемых бирж (асинхронно)
    await fetch_all_prices()
    
    # Указываем список путей к JSON-файлам с ценами по биржам
    filenames = [
        'data/price/bybit_price.json', 
        'data/price/gateio_price.json', 
        'data/price/huobi_price.json', 
        'data/price/kucoin_price.json', 
        'data/price/mexc_price.json', 
        'data/price/okex_price.json']
    
    # Убираем из списка несуществующие файлы, чтобы избежать ошибок
    filenames = [file for file in filenames if os.path.exists(file)]
    
    # Запускаем параллельно:
    # - поиск минимального ask
    # - поиск максимального bid
    # - расчёт арбитражного спреда
    await asyncio.gather(
        find_min_ask(filenames), 
        find_max_bid(filenames), 
        calculate_spread()
    )
    
    # Загружаем комиссии на вывод с каждой биржи (асинхронно)
    fees = await asyncio.gather(
        fetch_fees(okex),
        fetch_fees(gateio),
        fetch_fees(huobi),
        fetch_fees(mexc)
    )
    
    okex_fees, gateio_fees, huobi_fees, mexc_fees = fees
    
    # Обновляем данные: добавляем комиссии вывода и валидируем монеты
    new_data = update_fees(okex_fees, gateio_fees, huobi_fees, mexc_fees)
    
    # Удаляем записи, где спред не покрывает комиссии или данные невалидны
    delete_keys(new_data)
    
    # Сохраняем итоговый отфильтрованный словарь в main.json
    with open("data/main.json", "w") as f:
        json.dump(new_data, f) 
    print("Обновилось")

# Запуск асинхронного цикла событий, который запускает основной метод main()
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    finally:
        loop.close()
