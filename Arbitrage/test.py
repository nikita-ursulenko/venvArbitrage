import json

with open('test.json', 'r') as f:
    data = json.load(f)



import ccxt

def calculate_profit(exchange1_id, exchange2_id, symbol, amount_usdt, orderbook_limit=10):
    """
    Рассчитывает количества монет, которые можно купить на первой бирже за 100 USDT, 
    сколько можно получить USDT за продажу этих монет на второй бирже и является ли продажа выгодной.
    
    :param exchange1_id: идентификатор первой биржи
    :param exchange2_id: идентификатор второй биржи
    :param symbol: символ торговой пары
    :param amount_usdt: сумма в USDT, за которую мы хотим купить монеты на первой бирже
    :param orderbook_limit: глубина стакана ордеров
    :return: строка с результатом расчета
    """
    symbol +="/USDT"
    # Проверяем, является ли одна из бирж Кукоином
    if exchange1_id == "kucoin" or exchange2_id == "kucoin":
        # Если да, задаем лимит ордербука в 20
        orderbook_limit = 20

    # Создание экземпляров бирж
    exchange1 = getattr(ccxt, exchange1_id)()
    exchange2 = getattr(ccxt, exchange2_id)()

    # Запрос на получение текущего стакана ордеров на первой бирже
    orderbook_exchange1 = exchange1.fetch_order_book(symbol, orderbook_limit)
    asks_exchange1 = orderbook_exchange1['asks']

    # Оценка количества монет, которые можно купить на первой бирже
    coins_to_buy = 0  # количество монет
    usdt_spent = 0    # сумма денег, потраченных на покупку
    for ask_price, ask_volume in asks_exchange1:  # цикл по ордерам на продажу (asks)
        if usdt_spent + (ask_price * ask_volume) < amount_usdt:  # если еще не потрачено достаточно средств
            coins_to_buy += ask_volume  # увеличиваем количество монет, которые можно купить
            usdt_spent += ask_price * ask_volume  # добавляем потраченные деньги
        else: 
            # если потрачено достаточно средств, добавляем оставшуюся сумму монет деленное на цену
            coins_to_buy += (amount_usdt - usdt_spent) / ask_price  
            break   # выходим из цикла
      

    # Запрос на получение текущего стакана ордеров на второй бирже для определенного символа и лимита ордеров
    orderbook_exchange2 = exchange2.fetch_order_book(symbol, orderbook_limit)
    bids_exchange2 = orderbook_exchange2['bids']
    
    # Оценка количества монет, которые можно продать на второй бирже
    coins_to_sell = 0 # Инициализация количества монет, которые можно продать равным 0
    usdt_earned = 0 # Инициализация заработанных USDT равным 0
    for bid_price, bid_volume in bids_exchange2: # Перебор всех предложений на второй бирже
        if coins_to_sell + bid_volume < coins_to_buy:
            # Если общее количество монет, которые можно продать, меньше, чем количество монет, которые нужно купить,
            # добавляем объем этого предложения к общему количеству монет, которые можно продать, и обновляем заработанные USDT, умножив цену на монету на объем предложения
            coins_to_sell += bid_volume
            usdt_earned += bid_price * bid_volume  
        else:
            # Если общее количество монет, которые можно продать, больше или равно необходимому количеству монет,
            # вычисляем последний объем монет, который нужно продать для достижения требуемого количества покупки
            # добавляем заработанные USDT от продажи этого последнего объема монет к имеющимся заработанным USDT
            # обновляем количество монет, которые можно продать на равное количество монет, которые необходимо купить, и выходим из цикла
            last_to_sell = coins_to_buy - coins_to_sell
            usdt_earned += last_to_sell * bid_price
            coins_to_sell = coins_to_buy
            break
    
    
    

    # Определение, выгодна ли продажа монет на второй бирже
    # Итерация по валютам в данных и остановка цикла, когда найден соответствующий символ
    min_fee = None
    for currency in data:
        if data[currency]['symbol'] == symbol.replace("/USDT", ""):
            # Проверка, есть ли такса ask_fee для данной валюты
            if 'ask_fee' in data[currency]:           
                # Итерация по текущим затратам валюты
                for network, values in data[currency]['ask_fee'].items():
                    fees = []
                    # Если ключ 'withdraw' существует, добавьте комиссию за вывод средств в список комиссий
                    if 'withdraw' in values:
                        fees.append(values['withdraw']['fee'])
                # Установите минимальную комиссию как самую маленькую комиссию из списка комиссий
                min_fee = min(fees)                
            # Остановка цикла после нахождения соответствующей валюты     
            break
    

    exchange_urls = {
        "gateio": {
            "withdraw": f'https://www.gate.io/ru/myaccount/withdraw/{{symbol}}\n',
            "trade": f'https://www.gate.io/ru/trade/{{symbol}}_USDT\n',
            "deposit": f'https://www.gate.io/ru/myaccount/deposit/{{symbol}}\n'
        },
        "huobi": {
            "withdraw": f'https://www.huobi.com/en-us/finance/withdraw/{{symbol}}\n'.lower(),
            "trade": f'https://www.huobi.com/en-us/exchange/{{symbol}}_usdt\n'.lower(),
            "deposit": f'https://www.huobi.com/en-us/finance/deposit/{{symbol}}\n'.lower()
        },
        "kucoin": {
            "withdraw": f'https://www.kucoin.com/ru/assets/withdraw/{{symbol}}\n',
            "trade": f'https://www.kucoin.com/ru/trade/{{symbol}}-USDT\n',
            "deposit": f'https://www.kucoin.com/ru/assets/coin/{{symbol}}\n'
        },
        "okex": {
            "withdraw": f'https://www.okx.com/ru/balance/withdrawal/{{symbol}}-chain\n',
            "trade": f'https://www.okx.com/ru/trade-spot/{{symbol}}-usdt\n',
            "deposit": f'https://www.okx.com/ru/balance/recharge/{{symbol}}\n'
        },
        "mexc": {
            "withdraw": f'https://www.mexc.com/ru-RU/assets/withdraw/{{symbol}}\n',
            "trade": f'https://www.mexc.com/ru-RU/exchange/{{symbol}}_USDT\n',
            "deposit": f'https://www.mexc.com/ru-RU/assets/deposit/{{symbol}}\n'
        },
        "bybit": {
            "withdraw": f'https://www.bybit.com/user/assets/home/spot\n',
            "trade": f'https://www.bybit.com/ru-RU/trade/spot/{{symbol}}/USDT\n',
            "deposit": f'https://www.bybit.com/user/assets/home/spot\n'
        }
    }
    if min_fee:
        if usdt_earned - min_fee > amount_usdt * (1 + 0.002):
            print(exchange1_id,"->",exchange2_id)
            symbol = symbol.replace("/USDT", "")
            result = f"Купить {exchange1.id} {coins_to_buy:.2f} монет {symbol} за {amount_usdt:.2f} USDT.\n"
            
            if exchange1_id in exchange_urls:
                urls = exchange_urls[exchange1_id]
                result += urls["withdraw"].format(symbol=symbol).lower()
                result += urls["trade"].format(symbol=symbol).lower()
        
            result += f"C учетом комисии\nПродать {exchange2.id} можно продать {coins_to_sell:.2f} монет {symbol} за {usdt_earned:.2f} USDT и получить выгоду в {(usdt_earned - amount_usdt):.2f} USDT.\n"
        
            if exchange2_id in exchange_urls:
                urls = exchange_urls[exchange2_id]
                result += urls["deposit"].format(symbol=symbol).lower()
                result += urls["trade"].format(symbol=symbol).lower()
        else:
            result = ""
    else:
        if usdt_earned  > amount_usdt * (1 + 0.002):
            print(exchange1_id,"->",exchange2_id)
            symbol = symbol.replace("/USDT", "")
            result = f"Купить {exchange1.id} {coins_to_buy:.2f} монет {symbol} за {amount_usdt:.2f} USDT.\n"
            if exchange1_id in exchange_urls:
                urls = exchange_urls[exchange1_id]
                result += urls["withdraw"].format(symbol=symbol).lower()
                result += urls["trade"].format(symbol=symbol).lower()

            result += f"Нет данных о комисии\nПродать {exchange2.id} можно продать {coins_to_sell:.2f} монет {symbol} за {usdt_earned:.2f} USDT и получить выгоду в {(usdt_earned - amount_usdt):.2f} USDT.\n"
            if exchange2_id in exchange_urls:
                urls = exchange_urls[exchange2_id]
                result += urls["deposit"].format(symbol=symbol).lower()
                result += urls["trade"].format(symbol=symbol).lower()
        else:
            result = ""

    return result



import concurrent.futures

def process_item(key, value):
    # Получаем параметры из текущей записи
    ask_name = ""
    bid_name = ""
    symbol = value['symbol']
    if value['ask_name'] == "Gateio":
        ask_name = "gateio"
    if value['bid_name'] == "Gateio":
        bid_name = "gateio"
    if value['ask_name'] == "KuCoin":
        ask_name = "kucoin"
    if value['bid_name'] == "KuCoin":
        bid_name = "kucoin"
    if value['bid_name'] == "MEXC":
        bid_name = "mexc"
    if value['ask_name'] == "MEXC":
        ask_name = "mexc"
    if value['bid_name'] == "ByBit":
        bid_name = "bybit"
    if value['ask_name'] == "ByBit":
        ask_name = "bybit"
    if value['bid_name'] == "OKEX":
        bid_name = "okex"
    if value['ask_name'] == "OKEX":
        ask_name = "okex"
    if value['bid_name'] == "Huobi":
        bid_name = "huobi"
    if value['ask_name'] == "Huobi":
        ask_name = "huobi"

    if ask_name and bid_name:   # Если обе переменные указаны
            result = calculate_profit(ask_name, bid_name, symbol, 100, 5)   # Вызываем функцию calculate_profit()
            return result   # Возвращаем результат функции

def process_data(data):
    # Создание объекта ThreadPoolExecutor с использованием диспетчера потоков по умолчанию
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Создание списка futures, каждый из которых ассоциирован с элементом словаря data
        # Для каждого ключа-значения создается новый future методом submit()
        futures = [executor.submit(process_item, key, value) for key, value in data.items()]
        # Обработка завершенных futures с помощью as_completed()
        for future in concurrent.futures.as_completed(futures):
            # Получение результата выполнения соответствующего future
            result = future.result()
            # Если результат не равен None, выводим его на экран
            if result:
                print(result)


# Использование функции
process_data(data)