# ------------------------------------------
# Файл: spread.py (core)
# Назначение: Вычисление арбитражного спреда между биржами на основе сохранённых
# цен в формате JSON. Сравниваются ask (минимальные цены покупки) и bid (максимальные цены продажи).
# Результаты сохраняются в spreads.json, если спред находится в заданном диапазоне (1%–9%).
# ------------------------------------------

import json
import os

# Поиск минимальных цен ask по всем файлам и сохранение лучших предложений
# для каждой монеты, если она встречается на более чем одной бирже.
async def find_min_ask(filenames):
    key_values = {}
    for filename in filenames:
        # Открываем очередной JSON-файл, содержащий цены монет на конкретной бирже
        with open(filename, 'r') as f:
            data = json.load(f)
            for key in data:
                # Проходим по всем монетам внутри текущего файла
                if key not in key_values:
                    key_values[key] = {'min_ask': None, 'min_ask_file': None}
                # Если у монеты есть поле ask — начинаем сравнение
                if 'ask' in data[key]:
                    if data[key]['ask'] is not None:
                        ask = data[key]['ask']
                        if key_values[key]['min_ask'] is None or ask < key_values[key]['min_ask']:
                            key_values[key]['min_ask'] = ask
                            key_values[key]['min_ask_file'] = filename

    # Найти максимальное значение "ask" для каждого ключа и файл, в котором оно было найдено
    result = {}
    for key in key_values:
        min_ask = key_values[key]['min_ask']
        min_ask_file = key_values[key]['min_ask_file']
        # Проверить, был ли ключ найден в нескольких файлах
        num_files = sum(1 for filename in filenames if key in json.load(open(filename, 'r')))
        if min_ask_file == "data/price/bybit_price.json":
            name = "ByBit"
        elif min_ask_file == "data/price/okex_price.json":
            name = "OKEX"
        elif min_ask_file == "data/price/kucoin_price.json":
            name = "KuCoin"
        elif min_ask_file == "data/price/huobi_price.json":
            name = "Huobi"
        elif min_ask_file == "data/price/mexc_price.json":
            name = "MEXC"
        elif min_ask_file == "data/price/gateio_price.json":
            name = "Gateio"
        if min_ask is not None and num_files > 1:
            result[key] = {
                'name': name,
                'ask': min_ask
            }

    with open("data/spread/min_ask.json", "w") as f:
        json.dump(result, f)

# Поиск максимальных цен bid по всем файлам и сохранение лучших цен продажи
# для каждой монеты, если она торгуется на нескольких биржах.
async def find_max_bid(filenames):
    key_values = {}
    for filename in filenames:
        # Загружаем файл с данными по ценам монет с биржи
        with open(filename, 'r') as f:
            data = json.load(f)
            for key in data:
                if key not in key_values:
                    key_values[key] = {'max_bid': None, 'max_bid_file': None}
                # Если указана цена bid для монеты — обновляем при необходимости
                if 'bid' in data[key]:
                    if data[key]['bid'] is not None:
                        bid = data[key]['bid']
                        if key_values[key]['max_bid'] is None or bid > key_values[key]['max_bid']:
                            key_values[key]['max_bid'] = bid
                            key_values[key]['max_bid_file'] = filename

    # Найти максимальное значение "bid" для каждого ключа и файл, в котором оно было найдено
    result = {}
    for key in key_values:
        max_bid = key_values[key]['max_bid']
        max_bid_file = key_values[key]['max_bid_file']
        # Проверить, был ли ключ найден в нескольких файлах
        num_files = sum(1 for filename in filenames if key in json.load(open(filename, 'r')))
        if max_bid_file == "data/price/bybit_price.json":
            name = "ByBit"
        elif max_bid_file == "data/price/okex_price.json":
            name = "OKEX"
        elif max_bid_file == "data/price/kucoin_price.json":
            name = "KuCoin"
        elif max_bid_file == "data/price/huobi_price.json":
            name = "Huobi"
        elif max_bid_file == "data/price/mexc_price.json":
            name = "MEXC"
        elif max_bid_file == "data/price/gateio_price.json":
            name = "Gateio"
        if max_bid is not None and num_files > 1:
            result[key] = {
                'name': name,
                'bid': max_bid
            }

    with open("data/spread/max_bid.json", "w") as f:
        json.dump(result, f)

# Сравнение ask и bid цен, вычисление спреда (в процентах), сортировка и сохранение
# только тех монет, у которых спред от 1% до 9% — т.е. потенциально выгодный арбитраж.
async def calculate_spread():
    with open("data/spread/min_ask.json", "r") as f:
        min_ask_data = json.load(f)

    with open("data/spread/max_bid.json", "r") as f:
        max_bid_data = json.load(f)

    # Найти общие ключи в обоих файлах
    common_keys = set(min_ask_data.keys()).intersection(set(max_bid_data.keys()))

    # Обрабатываем каждую монету, которая присутствует и в ask, и в bid
    spread_list = []
    for key in common_keys:
        min_ask = min_ask_data[key]['ask']
        max_bid = max_bid_data[key]['bid']
        # Считаем среднюю цену между ask и bid, а также сам спред
        average = (max_bid + min_ask) / 2
        spread = max_bid - min_ask
        spread_procent = (spread / average) * 100 
        if 9 > spread_procent > 1:
            spread_list.append({
                'spread_percent': round(spread_procent, 2),
                'symbol': key.split('/')[0],
                'ask_name': min_ask_data[key]['name'],
                'ask': min_ask,
                'bid_name': max_bid_data[key]['name'],
                'bid': max_bid
            })

    # Сортировать список по возрастанию спреда
    sorted_spread_list = sorted(spread_list, key=lambda x: x['spread_percent'], reverse=True)

    # Преобразуем список результатов в словарь, где ключ — строка с процентом
    result = {f"{item['spread_percent']}%": item for item in sorted_spread_list}
    
    os.makedirs("data/spread", exist_ok=True)
    # Сохранить результат в файл
    with open("data/spread/spreads.json", "w") as f:
        json.dump(result, f)
