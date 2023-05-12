import json
import ccxt.async_support as ccxt
import asyncio
import time
import requests
import base64
import hashlib
import hmac

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
                value["ask_fee"] = None
        if "OKEX" in value["bid_name"]:
            symbol = value["symbol"]
            fees = okex_fees.get(symbol)
            info = fees["info"][symbol]
            #Если можно торговать и пополнять
            if info["canInternal"] and info["canDep"]:
                networks = fees["networks"]
                value["bid_fee"] = list(networks.keys())
            else:
                value["bid_fee"] = None
            
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
                    value["ask_fee"] = networks
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

async def main():
    fees = await asyncio.gather(
        fetch_fees(okex),
        fetch_fees(gateio),
        fetch_fees(huobi),
        fetch_fees(mexc)
    )
    okex_fees, gateio_fees, huobi_fees, mexc_fees = fees
    new_data = update_fees(okex_fees, gateio_fees, huobi_fees, mexc_fees)
    with open("test.json", "w") as f:
        json.dump(new_data, f)   

asyncio.run(main())

