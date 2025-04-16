#Kucoin -PRICE, FILTER
import json
import aiohttp


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

            import os; os.makedirs("data/price", exist_ok=True)
            with open("data/price/kucoin_price.json", "w") as f:
                json.dump(tickers, f)
            os.makedirs("data/fees", exist_ok=True)
            with open("data/fees/kucoin_fees.json", "w") as f:
                json.dump(fees, f)
     