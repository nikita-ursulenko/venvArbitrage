import json

# Load the JSON file into a dictionary object
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

    if exchange1_id == "kucoin" or exchange2_id == "kucoin":
        orderbook_limit = 20

    # Создание экземпляров бирж
    exchange1 = getattr(ccxt, exchange1_id)()
    exchange2 = getattr(ccxt, exchange2_id)()

    # Запрос на получение текущего стакана ордеров на первой бирже
    orderbook_exchange1 = exchange1.fetch_order_book(symbol, orderbook_limit)
    asks_exchange1 = orderbook_exchange1['bids']

   # Оценка количества монет, которые можно купить на первой бирже
    coins_to_buy = 0
    usdt_spent = 0
    for ask_price, ask_volume in asks_exchange1:
        if usdt_spent + (ask_price * ask_volume) < amount_usdt:
            coins_to_buy += ask_volume
            usdt_spent += ask_price * ask_volume
        else: 
            coins_to_buy += (amount_usdt - usdt_spent) / ask_price
            break

   # fee = 0 
    #for key in data:
       # if data[key]['symbol'] == symbol.replace("/USDT", ""):
       #     if data[key]['ask_fee']:
       #         fees = data[key]['ask_fee']
       #         print(symbol)
       #         print(fees)


                

             
    # Запрос на получение текущей цены продажи монет на второй бирже
    ticker_exchange2 = exchange2.fetch_ticker(symbol)
    bid_price_exchange2 = ticker_exchange2['ask']

    

     # Запрос на получение текущего стакана ордеров на второй бирже
    orderbook_exchange2 = exchange2.fetch_order_book(symbol, orderbook_limit)
    bids_exchange2 = orderbook_exchange2['asks']

    # Оценка количества монет, которые можно продать на второй бирже
    coins_to_sell = 0
    usdt_earned = 0
    for bid_price, bid_volume in bids_exchange2:
        if coins_to_sell + bid_volume < coins_to_buy:
            coins_to_sell += bid_volume
            usdt_earned += bid_price * bid_volume  
        else:
            last_to_sell = coins_to_buy - coins_to_sell
            usdt_earned += last_to_sell * bid_price
            coins_to_sell = coins_to_buy
            break
    
    

    # Определение, выгодна ли продажа монет на второй бирже

    if usdt_earned  > amount_usdt:
        symbol = symbol.replace("/USDT", "")
        result = f"\nКупить {exchange1.id} {coins_to_buy:.2f} монет {symbol} за {amount_usdt:.2f} USDT.\n"
        #if {exchange1.id} contains the string 'gateio', then we add the print https://www.gate.io/ru/myaccount/withdraw/{symbol} to the result
        if exchange1_id == "gateio":
            #symbol without /USDT
            result +=(f'https://www.gate.io/ru/myaccount/withdraw/{symbol}\n')
            result +=(f'https://www.gate.io/ru/trade/{symbol}_USDT\n')
        if exchange1_id == "huobi":
            #symbol without /USDT
            result +=(f'https://www.huobi.com/en-us/finance/withdraw/{symbol}\n'.lower())
            result +=(f'https://www.huobi.com/en-us/exchange/{symbol}_usdt\n'.lower())
        if exchange1_id == "kucoin":
            #symbol without /USDT
            result +=(f'https://www.kucoin.com/ru/assets/withdraw/{symbol}\n')
            result +=(f'https://www.kucoin.com/ru/trade/{symbol}-USDT\n')
        if exchange1_id == "okex":
            #symbol without /USDT
            result +=(f'https://www.okx.com/ru/balance/withdrawal/{symbol}-chain\n')
            result +=(f'https://www.okx.com/ru/trade-spot/{symbol}-usdt\n')
        if exchange1_id == "mexc":
            #symbol without /USDT
            result +=(f'https://www.mexc.com/ru-RU/assets/withdraw/{symbol}\n')
            result +=(f'https://www.mexc.com/ru-RU/exchange/{symbol}_USDT\n')
        if exchange1_id == "bybit":
            #symbol without /USDT
            result +=(f'https://www.bybit.com/user/assets/home/spot\n')
            result +=(f'https://www.bybit.com/ru-RU/trade/spot/{symbol}/USDT\n')
        result += f"Продать {exchange2.id} можно продать {coins_to_sell:.2f} монет {symbol} за {usdt_earned:.2f} USDT и получить выгоду в {(usdt_earned - amount_usdt):.2f} USDT.\n"
        if exchange2_id == "gateio":
            #symbol without /USDT
            symbol = symbol.replace("/USDT", "")
            result +=(f'https://www.gate.io/ru/myaccount/deposit/{symbol}\n')
            result +=(f'https://www.gate.io/ru/trade/{symbol}_USDT\n')
        if exchange2_id == "huobi":
            #symbol without /USDT
            result +=(f'https://www.huobi.com/en-us/finance/deposit/{symbol}\n'.lower())
            result +=(f'https://www.huobi.com/en-us/exchange/{symbol}_usdt\n'.lower())
        if exchange2_id == "kucoin":
            #symbol without /USDT
            result +=(f'https://www.kucoin.com/ru/assets/coin/{symbol}\n')
            result +=(f'https://www.kucoin.com/ru/trade/{symbol}-USDT\n')
        if exchange2_id == "okex":
            #symbol without /USDT
            result +=(f'https://www.okx.com/ru/balance/recharge/{symbol}\n')
            result +=(f'https://www.okx.com/ru/trade-spot/{symbol}-usdt\n')
        if exchange2_id == "mexc":
            #symbol without /USDT
            result +=(f'https://www.mexc.com/ru-RU/assets/deposit/{symbol}\n')
            result +=(f'https://www.mexc.com/ru-RU/exchange/{symbol}_USDT\n')
        if exchange2_id == "bybit":
            #symbol without /USDT
            result +=(f'https://www.bybit.com/user/assets/home/spot\n')
            result +=(f'https://www.bybit.com/ru-RU/trade/spot/{symbol}/USDT\n')
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

    if ask_name and bid_name:
        result = calculate_profit(ask_name, bid_name, symbol, 95, 5)
        return result

def process_data(data):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_item, key, value) for key, value in data.items()]
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                print(result)

# Использование функции
process_data(data)