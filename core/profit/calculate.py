# ------------------------------------------
# Файл: calculate.py (core/profit)
# Назначение: содержит основную бизнес-логику арбитража.
# Функция calculate_profit рассчитывает потенциальную прибыль между двумя биржами
# путём симуляции покупки монеты на одной и её продажи на другой, основываясь на ордерах.
# Также генерирует текстовый результат с ссылками на биржи.
# process_item — вспомогательная функция, подготавливающая данные и вызывающая расчет.
# ------------------------------------------
import ccxt  # библиотека для подключения к API криптовалютных бирж

def calculate_profit(exchange1_id, exchange2_id, symbol, amount_usdt, orderbook_limit=10):
    """
    Рассчитывает потенциальную прибыль при арбитраже между двумя биржами.
    Покупает монету на первой бирже и продаёт на второй, используя ордербуки.
    :param exchange1_id: идентификатор первой биржи
    :param exchange2_id: идентификатор второй биржи
    :param symbol: символ торговой пары
    :param amount_usdt: сумма в USDT, за которую мы хотим купить монеты на первой бирже
    :param orderbook_limit: глубина стакана ордеров
    :return: строка с результатом расчета
    """
    symbol += "/USDT"  # добавляем суффикс к паре, чтобы привести к формату биржи (например BTC → BTC/USDT)

    # Создаем экземпляры бирж по их идентификатору (названию)
    exchange1 = getattr(ccxt, exchange1_id)()
    exchange2 = getattr(ccxt, exchange2_id)()

    # Получаем ордербук первой биржи (цены, по которым можно купить монету)
    orderbook_exchange1 = exchange1.fetch_order_book(symbol, orderbook_limit)
    asks_exchange1 = orderbook_exchange1['asks']

    # Считаем, сколько монет мы можем купить на указанную сумму USDT
    coins_to_buy = 0
    usdt_spent = 0
    for ask_price, ask_volume in asks_exchange1:
        if usdt_spent + (ask_price * ask_volume) < amount_usdt:
            coins_to_buy += ask_volume
            usdt_spent += ask_price * ask_volume
        else:
            coins_to_buy += (amount_usdt - usdt_spent) / ask_price
            break

    # Получаем тикер второй биржи — цену, по которой готовы покупать монету
    ticker_exchange2 = exchange2.fetch_ticker(symbol)
    bid_price_exchange2 = ticker_exchange2['bid']

    # Получаем ордербук второй биржи (цены, по которым мы можем продать монету)
    orderbook_exchange2 = exchange2.fetch_order_book(symbol, orderbook_limit)
    bids_exchange2 = orderbook_exchange2['bids']

    # Считаем, сколько USDT можно выручить за купленные монеты на второй бирже
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

    # Если сделка выгодна — формируем текст с результатами
    if usdt_earned > amount_usdt:
        symbol = symbol.replace("/USDT", "")
        result = f"\nКупить {exchange1.id} {coins_to_buy:.2f} монет {symbol} за {amount_usdt:.2f} USDT.\n"

        # Добавляем ссылки на интерфейсы покупки/вывода для первой биржи
        if exchange1_id == "gateio":
            result += f'https://www.gate.io/ru/myaccount/withdraw/{symbol}\n'
            result += f'https://www.gate.io/ru/trade/{symbol}_USDT\n'
        if exchange1_id == "huobi":
            result += f'https://www.huobi.com/en-us/finance/withdraw/{symbol}\n'
            result += f'https://www.huobi.com/en-us/exchange/{symbol}_usdt\n'
        if exchange1_id == "kucoin":
            result += f'https://www.kucoin.com/ru/assets/coin/{symbol}\n'
            result += f'https://www.kucoin.com/ru/trade/{symbol}-USDT\n'
        if exchange1_id == "okex":
            result += f'https://www.okx.com/ru/balance/withdrawal/{symbol}-chain\n'
            result += f'https://www.okx.com/ru/trade-spot/{symbol}-usdt\n'
        if exchange1_id == "mexc":
            result += f'https://www.mexc.com/ru-RU/assets/withdraw/{symbol}\n'
            result += f'https://www.mexc.com/ru-RU/exchange/{symbol}_USDT\n'
        if exchange1_id == "bybit":
            result += f'https://www.bybit.com/user/assets/home/spot\n'
            result += f'https://www.bybit.com/ru-RU/trade/spot/{symbol}/USDT\n'

        # Добавляем текст о продаже на второй бирже
        result += f"\nПродать {exchange2.id} можно продать {coins_to_sell:.2f} монет {symbol} за {usdt_earned:.2f} USDT и получить выгоду в {(usdt_earned - amount_usdt):.2f} USDT.\n"

        # Добавляем ссылки на интерфейсы ввода/торговли на второй бирже
        if exchange2_id == "gateio":
            result += f'https://www.gate.io/ru/myaccount/deposit/{symbol}\n'
            result += f'https://www.gate.io/ru/trade/{symbol}_USDT\n'
        if exchange2_id == "huobi":
            result += f'https://www.huobi.com/en-us/finance/deposit/{symbol}\n'
            result += f'https://www.huobi.com/en-us/exchange/{symbol}_usdt\n'
        if exchange2_id == "kucoin":
            result += f'https://www.kucoin.com/ru/assets/withdraw/{symbol}\n'
            result += f'https://www.kucoin.com/ru/trade/{symbol}-USDT\n'
        if exchange2_id == "okex":
            result += f'https://www.okx.com/ru/balance/recharge/{symbol}\n'
            result += f'https://www.okx.com/ru/trade-spot/{symbol}-usdt\n'
        if exchange2_id == "mexc":
            result += f'https://www.mexc.com/ru-RU/assets/deposit/{symbol}\n'
            result += f'https://www.mexc.com/ru-RU/exchange/{symbol}_USDT\n'
        if exchange2_id == "bybit":
            result += f'https://www.bybit.com/user/assets/home/spot\n'
            result += f'https://www.bybit.com/ru-RU/trade/spot/{symbol}/USDT\n'
    else:
        result = ""  # сделка невыгодна — не возвращаем ничего

    return result

# Функция для обработки одного элемента из данных — вытаскивает символ и биржи, вызывает расчет
def process_item(key, value, amount_usdt):
    symbol = value['symbol']  # символ монеты (например BTC)

    # Словарь преобразования названий из JSON в формат ccxt
    exchange_map = {
        "Gateio": "gateio",
        "KuCoin": "kucoin",
        "MEXC": "mexc",
        "ByBit": "bybit",
        "OKEX": "okex",
        "Huobi": "huobi"
    }

    # Получаем id бирж для покупки и продажи
    ask_name = exchange_map.get(value.get("ask_name"), "")
    bid_name = exchange_map.get(value.get("bid_name"), "")

    # Если обе биржи определены — вызываем расчет
    if ask_name and bid_name:
        result = calculate_profit(ask_name, bid_name, symbol, amount_usdt, 20)
        return result