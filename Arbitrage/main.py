import asyncio
import json
import aiohttp
import ccxt.async_support as ccxt
from web3 import Web3, HTTPProvider
import subprocess
import time
import requests
import base64
import hashlib
import hmac

#Gateio -PRICE, FILTER
async def gateio_price():
#+Чистый код без CCXT
#+Хороший фильтр на валидность монет
    gateio = "https://api.gateio.ws/api/v4/spot"
    tickers = "/tickers"
    currencies = "/currencies"
    async with aiohttp.ClientSession() as session:
        async with session.get(gateio + tickers) as response:
            coin_list_gateio = []
            data = await response.json()
            #Все пары с _USDT
            usdt_pairs = [pair for pair in data if "_USDT" in pair["currency_pair"]]
            #Все имена монет без _USDT
            coins = [pair["currency_pair"].split("_")[0] for pair in usdt_pairs]
            
            async with session.get(gateio + currencies) as url_currencies:
                coin_chains = await url_currencies.json()
                
                #Начинаем выводить только те монеты которые доступны для всех операций 
                for coin in coins:
                    for chain in coin_chains:
                        #Если есть в списке далее фильтр на доступность 1 вывод 2 пополнение 3 торговлю
                        if chain["currency"] == coin and not chain["delisted"] and not chain["withdraw_disabled"] and not chain["withdraw_delayed"] and not chain["deposit_disabled"] and not chain["trade_disabled"]:
                                # Добавляем найденое (Сеть перевода и вывод)
                            coin_list_gateio.append(chain["currency"])

                    # Обработка цен на монеты
                coin_dict_gateio_price = {}
                with open("price/gateio_price.json", "w") as f:
                    for coin in coin_list_gateio:
                        for pair in usdt_pairs:
                            if pair["currency_pair"] == coin+"_USDT":
                                coin_dict_gateio_price[coin+"/USDT"] = {
                                    "last": float(pair["last"]),
                                    # Продают
                                    "ask": float(pair["lowest_ask"]),
                                    # Покупают
                                    "bid": float(pair["highest_bid"])
                                }
                    json.dump(coin_dict_gateio_price, f)

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
    with open("price/okex_price.json", "w") as f:
        json.dump(pairs_info, f)

    await exchange.close()

#Kucoin -PRICE, FILTER
async def kucoin_price():
#+Хороший фильтр на валидность монет
#+Чистый код без CCXT 
#+Сразу импортирует fees 
    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.kucoin.com/api/v1/currencies') as response:
            data = await response.json()
            pairs = []
            for currency in data['data']:
                #Если монетой можно 1 торговать  2 снять и  3 пополнять
                if currency['isDebitEnabled'] and currency['isWithdrawEnabled'] and currency['isDepositEnabled']:
                    pairs.append(currency)
            #Делаю tickers обьектом
            tickers = {}
            #Fees надо будет поменять на обьект но пока оставил масивом
            fees = []
            async with session.get('https://api.kucoin.com/api/v1/market/allTickers') as response:
                data = await response.json()
                #Из всех актуальных выбрал только USDT и сохранил только 3 значение 
                for ticker in data['data']['ticker']:
                    if ticker['symbol'] in [f"{pair['currency']}-USDT" for pair in pairs]:
                        #split оставляю только символы
                        currency = ticker['symbol'].split('-')[0]
                        #обьявляю ключ и его значения
                        tickers[currency+"/USDT"] = {
                            'last': float(ticker['last']),
                            'ask': float(ticker['buy']),
                            'bid': float(ticker['sell'])

                        }
                        # Определяю кол-во пар 
                        for i in range(len(pairs)):
                            #если начинается на так же как другие монеты то заходим в if
                            if pairs[i]['currency'].startswith(currency):
                                symbol = pairs[i]['currency']
                                #Перевожу в инт и округляю до 2 после запятых
                                with_fees = round(float(pairs[i]['withdrawalMinFee']) * float(ticker['last']), 2)
                                #временный код надо будет поменять его на обьект
                                fees.append({'symbol': symbol, 
                                             'with_fees': with_fees})

            with open("price/kucoin_price.json", "w") as f:
                json.dump(tickers, f)
            with open("fees/kucoin_fees.json", "w") as f:
                json.dump(fees, f)
        
async def bybit_price():
    exchange = ccxt.bybit({
        'enableRateLimit': True,
    })
    
    try:
        markets = await exchange.load_markets()
        pairs = [symbol for symbol in markets if '/USDT' in symbol and markets[symbol]['spot'] and markets[symbol]['active']]
        
        tickers = await exchange.fetch_tickers(pairs)
        
        data = {}
        for symbol, ticker in tickers.items():
            data[symbol] = {
                'last': ticker['last'],
                'ask': ticker['ask'],
                'bid': ticker['bid'],
            }
        
        with open('price/bybit_price.json', 'w') as f:
            json.dump(data, f)
            
    except Exception as e:
        print('Error Bybit occurred:', e)
        
    finally:
        await exchange.close()
        
async def huobi_price():
    exchange = ccxt.huobi({
        'enableRateLimit': True,
    })
    
    try:
        markets = await exchange.load_markets()
        pairs = [symbol for symbol in markets if '/USDT' in symbol and markets[symbol]['spot'] and markets[symbol]['active']]
        
        tickers = await exchange.fetch_tickers(pairs)
        
        data = {}
        for symbol, ticker in tickers.items():
            data[symbol] = {
                'last': ticker['last'],
                'ask': ticker['ask'],
                'bid': ticker['bid'],
            }
        
        with open('price/huobi_price.json', 'w') as f:
            json.dump(data, f)
            
    except Exception as e:
        print('Error huobi occurred:', e)
        
    finally:
        await exchange.close()
        
async def mexc_price():
    exchange = ccxt.mexc({
        'enableRateLimit': True,
    })
    
    try:
        markets = await exchange.load_markets()
        pairs = [symbol for symbol in markets if '/USDT' in symbol and markets[symbol]['spot'] and markets[symbol]['active']]

        tickers = await exchange.fetch_tickers(pairs)
        data = {}
        for symbol, ticker in tickers.items():
            if ticker['ask'] is None:
                continue
            data[symbol] = {
                'last': ticker['last'],
                'ask': ticker['ask'],
                'bid': ticker['bid'],
            }
        
        with open('price/mexc_price.json', 'w') as f:
            json.dump(data, f)
            
    except Exception as e:
        print('Error mexc occurred:', e)
        
    finally:
        await exchange.close()
        
#Вычисляем спред------------------------

async def find_min_ask(filenames):
    key_values = {}
    for filename in filenames:
        with open(filename, 'r') as f:
            data = json.load(f)
            for key in data:
                if key not in key_values:
                    key_values[key] = {'min_ask': None, 'min_ask_file': None}
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
        if min_ask_file == "price/bybit_price.json":
            name = "ByBit"
        elif min_ask_file == "price/okex_price.json":
            name = "OKEX"
        elif min_ask_file == "price/kucoin_price.json":
            name = "KuCoin"
        elif min_ask_file == "price/huobi_price.json":
            name = "Huobi"
        elif min_ask_file == "price/mexc_price.json":
            name = "MEXC"
        elif min_ask_file == "price/gateio_price.json":
            name = "Gateio"
        if min_ask is not None and num_files > 1:
            result[key] = {
                'name': name,
                'ask': min_ask
            }

    with open("spread/min_ask.json", "w") as f:
        json.dump(result, f)

async def find_max_bid(filenames):
    key_values = {}
    for filename in filenames:
        with open(filename, 'r') as f:
            data = json.load(f)
            for key in data:
                if key not in key_values:
                    key_values[key] = {'max_bid': None, 'max_bid_file': None}
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
        if max_bid_file == "price/bybit_price.json":
            name = "ByBit"
        elif max_bid_file == "price/okex_price.json":
            name = "OKEX"
        elif max_bid_file == "price/kucoin_price.json":
            name = "KuCoin"
        elif max_bid_file == "price/huobi_price.json":
            name = "Huobi"
        elif max_bid_file == "price/mexc_price.json":
            name = "MEXC"
        elif max_bid_file == "price/gateio_price.json":
            name = "Gateio"
        if max_bid is not None and num_files > 1:
            result[key] = {
                'name': name,
                'bid': max_bid
            }

    with open("spread/max_bid.json", "w") as f:
        json.dump(result, f)

async def calculate_spread():
    with open("spread/min_ask.json", "r") as f:
        min_ask_data = json.load(f)

    with open("spread/max_bid.json", "r") as f:
        max_bid_data = json.load(f)

    # Найти общие ключи в обоих файлах
    common_keys = set(min_ask_data.keys()).intersection(set(max_bid_data.keys()))

    # Вычислить спред для каждого общего ключа
    spread_list = []
    for key in common_keys:
        min_ask = min_ask_data[key]['ask']
        max_bid = max_bid_data[key]['bid']
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

    # Преобразовать список в словарь
    result = {f"{item['spread_percent']}%": item for item in sorted_spread_list}

    # Сохранить результат в файл
    with open("spread/spreads.json", "w") as f:
        json.dump(result, f)



#=====================================

okex = ccxt.okex({
    'apiKey': '8d7da0e1-33ac-42df-a10b-a33d213fc04c',
    'secret': 'E0B99AB061E85641E9751E0814EE63CC',
    'password': 'Bratuseni8!'
})
gateio = ccxt.gateio({
    'apiKey': 'ade074c8b80a28d3c39c00639dc86d68',
    'secret': '379da1d9c3a53cd9cd552cd391bf59ff30070cd6ee902e0a0274d3d692793080',
})
huobi = ccxt.huobi({
    'apiKey': 'dc91a823-e993b76d-vqgdf4gsga-257cb',
    'secret': 'e5b44080-0710e5ea-bfc49bb3-42730',
})
mexc = ccxt.mexc({
    'apiKey': 'mx0vglNTjPgS7EnOBI',
    'secret': '2f13ad3b58c741ae9dba48531b853db3',
})

def update_fees(okex_fees, gateio_fees, huobi_fees, mexc_fees):
    with open("spread/spreads.json", "r") as f:
        data = json.load(f)
    
    keys_to_delete = []
    for key, value in data.items():
        # OKEX ------------------------------
        #ASK в $ 
        if "OKEX" in value["ask_name"]:
            symbol = value["symbol"]
            fees = okex_fees.get(symbol)
            info = fees["info"][symbol]
            # Есть валидность на доступность вывода
            # FILTER
            if info["canInternal"] and info["canWd"]:
                networks = fees["networks"]
                for network in networks.keys():
                    networks[network]["withdraw"]["fee"] = value["ask"] * float(networks[network]["withdraw"]["fee"])
                value["ask_fee"] = networks
                #Выводим процент = 0 так как биржа не дает инфу
                value["ask_withdraw_percent"] = 0
            else:
                keys_to_delete.append(key)
        if "OKEX" in value["bid_name"]:
            symbol = value["symbol"]
            fees = okex_fees.get(symbol)
            info = fees["info"][symbol]
            #Если можно торговать и пополнять
            if info["canInternal"] and info["canDep"]:
                networks = fees["networks"]
                value["bid_fee"] = list(networks.keys())
            else:
                keys_to_delete.append(key)

            
        # GATEIO ------------------------------
        #ASK в $
        if "Gateio" in value["ask_name"]:
            symbol = value["symbol"]
            fees = gateio_fees.get(symbol)
            info = fees["info"]
            #Валидноть присутсвует в gateio_price(), выводим только актуальные монеты 
            #FILTER
            #Если дневной лимит больше 0 то выполняем дальше
            if float(info["withdraw_day_limit"]) > 0:
                #Обьявляем переменную 
                networks = fees["networks"]
                #Перебираем ключи переменной
                for network in networks.keys():
                    #Умножаем колво монет на цену(Для того чтобы знать в $ комиссию)
                    networks[network]["withdraw"]["fee"] = value["ask"] * float(networks[network]["withdraw"]["fee"])
                #Создаем ключ ASK_FEE и передаем туда все сети которые поддерживаются    
                value["ask_fee"] = networks
                #Если процент не пустой 
                if info["withdraw_percent"] != None:
                    #Создаем ключ и передаем значение 
                    value["ask_withdraw_percent"] = info["withdraw_percent"]
                #Иначе выводим 0
                else: value["ask_withdraw_percent"] = 0
            #Значит не можем вывести
            else: value["ask_fee"] = None
        if "Gateio" in value["bid_name"]:
            symbol = value["symbol"]
            fees = gateio_fees.get(symbol)
            if fees:
                info = fees["info"]
                if float(info["withdraw_day_limit"]) > 0:
                    networks = fees["networks"]
                    value["bid_fee"] = list(networks.keys())
            else: value["bid_fee"] = None
            
        # HUOBI ------------------------------
        #ASK в $
        if "Huobi" in value["ask_name"]:
            symbol = value["symbol"]
            fees = huobi_fees.get(symbol)
            if fees is not None:
                #Комиссия сетей
                chains = fees["info"].get("chains")
                if chains is not None:
                    networks = {}
                    for chain in chains:
                        #Если есть название то присваиваем 
                        if "baseChain" in chain:
                            network_name = chain["baseChain"]
                        #Иначе присваиваем другое имя 
                        else: network_name = chain["displayName"]
                        #Есть валидность на доступность вывода 
                        #FILTER
                        if chain["withdrawStatus"] != "prohibited":
                            withdraw = {}
                            fee = {}
                            #Выводим комиссию в $
                            if "transactFeeRateWithdraw" in chain:
                                fee_with = float(chain["transactFeeRateWithdraw"])
                            else: fee_with = float(chain["transactFeeWithdraw"])
                            fee["fee"] = round(fee_with * value["ask"], 1)
                            withdraw["withdraw"] = fee
                            networks[network_name] = withdraw
                        else:
                            keys_to_delete.append(key)

                    # Не передается по ccxt проценты поэтому = 0
                    value["ask_withdraw_percent"] = 0
                else:
                    value["ask_fee"] = None
        if "Huobi" in value["bid_name"]:
            symbol = value["symbol"]
            fees = huobi_fees.get(symbol)
            if fees is not None:
                chains = fees["info"].get("chains")
                if chains is not None:
                    networks = {}
                    for chain in chains:
                        if "baseChain" in chain:
                            network_name = chain["baseChain"]
                        else: network_name = chain["displayName"]
                        networks = fees["networks"]
                        if chain["depositStatus"] == "prohibited":
                            keys_to_delete.append(key)
                    value["bid_fee"] = list(networks.keys())
                else:
                    value["bid_fee"] = None

        # MEXC ------------------------------
        #ASK в $
        if "MEXC" in value["ask_name"]:
            symbol = value["symbol"]
            fees = mexc_fees.get(symbol)
            ask = value["ask"]
            if fees is not None:
                ask_fee = {}
                for network in fees["info"]["networkList"]:
                    if network.get("withdrawEnable") is True:
                        network_name = network.get("network")
                        network_fee = network.get("withdrawFee")
                        ask_fee[network_name] = {}
                        ask_fee[network_name]["withdraw"] = {}
                        ask_fee[network_name]["withdraw"]["fee"] = round(float(network_fee) * ask, 2)
                    else:
                        keys_to_delete.append(key)
                if ask_fee:
                    value["ask_fee"] = ask_fee
                    value["ask_withdraw_percent"] = None
                else:
                    value["ask_fee"] = None
        if "MEXC" in value["bid_name"]:
            symbol = value["symbol"]
            fees = mexc_fees.get(symbol)
            if fees is not None:
                bid_fee = {}
                for network in fees["info"]["networkList"]:
                    if network.get("depositEnable") is True:
                        network_name = network.get("network")
                        bid_fee[network_name] = {}
                    else:
                        keys_to_delete.append(key)
                if bid_fee:
                    value["bid_fee"] = list(bid_fee.keys())
                else:
                    value["bid_fee"] = None

        # KuCoin ------------------------------
        #ASK в $
        if "KuCoin" in value["ask_name"]:
            symbol = value["symbol"]
            ask = value["ask"]
            withdrawal_limits = get_fee_kucoin(symbol, ask)
            if "error" in withdrawal_limits:
                print(f"Error: {withdrawal_limits['error']}")
                continue
            value["ask_fee"] = withdrawal_limits
            time.sleep(0.6)
        if "KuCoin" in value["bid_name"]:
            symbol = value["symbol"]
            bid = value["bid"]
            withdrawal_limits = get_fee_kucoin(symbol, bid)
            if "error" in withdrawal_limits:
                print(f"Error: {withdrawal_limits['error']}")
                continue
            value["bid_fee"] = withdrawal_limits 
            time.sleep(0.6)
    
    #почистить массив от одинаковых значений

    
    
    for key in list(set(keys_to_delete)):
        del data[key]
    return data

def get_fee_kucoin(currency, value):
    # ваш публичный и секретный ключи KuCoin
    api_key = '644d099df55bbf0001db4458'
    api_secret = '35aa3110-d54d-4e06-9c70-bd4d5f6f96f1'
    api_passphrase = 'Bratuseni8!'

    # создание метки времени в миллисекундах
    nonce = str(int(time.time() * 1000))

    # формирование подписи запроса
    message = f'{nonce}GET/api/v1/withdrawals/quotas?currency={currency}'
    signature = base64.b64encode(hmac.new(api_secret.encode(), message.encode(), hashlib.sha256).digest()).decode()

    # формирование заголовков запроса
    headers = {
        'KC-API-KEY': api_key,
        'KC-API-SIGN': signature,
        'KC-API-TIMESTAMP': nonce,
        'KC-API-PASSPHRASE': api_passphrase
    }

    # выполнение запроса
    url = f'https://api.kucoin.com/api/v1/withdrawals/quotas?currency={currency}'
    response = requests.get(url, headers=headers)

    # обработка ответа
    if response.status_code == 200:
        withdrawals_data = response.json()
        fee = {}
        fees = {}
        withdraw = {}
        coin = withdrawals_data["data"]["currency"]
        withdraw["fee"] = round(float(withdrawals_data["data"]["withdrawMinFee"]) * value, 2)
        fees["withdraw"] = withdraw
        fee[coin] = fees
        return fee
    else:
        return {"error": response.text}

async def fetch_fees(exchange):
    try:
        fees = await exchange.fetch_deposit_withdraw_fees()
        return fees
    finally:
        await exchange.close()


def delete_keys(data):
    keys_to_delete = []
    for key, value in data.items():
        if value is not None and isinstance(value, dict):
            ask_fee = value.get('ask_fee', {})
            fee = 0
            if ask_fee:
                for currency, details in ask_fee.items():
                    withdraw = details.get('withdraw', {})
                    if withdraw:
                        fee = withdraw.get('fee', 0)

                        break

            spread_percent = value.get('spread_percent', 0)
            if spread_percent < fee * 1.3:
                keys_to_delete.append(key)
            if value.get('ask_withdraw_percent', 0):
                ask_withdraw_percent = value.get('ask_withdraw_percent', 0)
                # delete symbol % from ask_withdraw_percent
                ask_withdraw_percent = ask_withdraw_percent.replace("%", "")
                ask_withdraw_percent = float(ask_withdraw_percent)
                if ask_withdraw_percent > spread_percent:
                    if spread_percent > fee * 1.3:
                        keys_to_delete.append(key)


    for key in keys_to_delete:
        del data[key]

#================================

async def main():
    # Запускаем обе функции параллельно с помощью функции asyncio.gather
    await asyncio.gather(okex_price(), gateio_price(), kucoin_price(), bybit_price(), huobi_price(), mexc_price())
    filenames = ['price/bybit_price.json', 'price/gateio_price.json', 'price/huobi_price.json', 'price/kucoin_price.json', 'price/mexc_price.json', 'price/okex_price.json']
    await asyncio.gather(find_min_ask(filenames), find_max_bid(filenames), calculate_spread())
    fees = await asyncio.gather(
        fetch_fees(okex),
        fetch_fees(gateio),
        fetch_fees(huobi),
        fetch_fees(mexc)
    )
    okex_fees, gateio_fees, huobi_fees, mexc_fees = fees
    new_data = update_fees(okex_fees, gateio_fees, huobi_fees, mexc_fees)
    delete_keys(new_data)
    print("Обновилось")
    with open("test.json", "w") as f:
        json.dump(new_data, f) 

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    finally:
        loop.close()
