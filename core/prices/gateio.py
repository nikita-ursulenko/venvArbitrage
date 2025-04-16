# ------------------------------------------
# Файл: gateio.py (core/prices)
# Назначение: Асинхронная загрузка актуальных цен монет с биржи Gate.io без использования CCXT.
# Скрипт фильтрует только пары к USDT, проверяет доступность монет по статусу (торговля, ввод, вывод),
# и сохраняет их цену (last, ask, bid) в файл JSON.
# ------------------------------------------
import json  # используется для сохранения данных в JSON-файл
import aiohttp  # асинхронный HTTP-клиент
import os  # для создания директорий

# Асинхронная функция получения цен с биржи Gate.io
async def gateio_price():
    # ✅ Работаем без использования библиотеки CCXT — напрямую через API
    # ✅ Добавлен фильтр на монеты, доступные для торговли, пополнения и вывода

    gateio = "https://api.gateio.ws/api/v4/spot"  # базовый URL для спотовых запросов Gate.io
    tickers = "/tickers"  # эндпоинт получения цен всех пар
    currencies = "/currencies"  # эндпоинт получения статуса валют

    async with aiohttp.ClientSession() as session:
        # Загружаем все спотовые тикеры с биржи
        async with session.get(gateio + tickers) as response:
            coin_list_gateio = []  # список монет, которые будут включены после фильтрации
            data = await response.json()  # список всех валютных пар
            
            # Фильтруем только пары, торгуемые к USDT (например: BTC_USDT)
            usdt_pairs = [pair for pair in data if "_USDT" in pair["currency_pair"]]
            
            # Извлекаем только имена монет (например BTC из BTC_USDT)
            coins = [pair["currency_pair"].split("_")[0] for pair in usdt_pairs]
            
            # Загружаем список монет и их сетей, чтобы фильтровать по статусу
            async with session.get(gateio + currencies) as url_currencies:
                coin_chains = await url_currencies.json()
                
                # Проходим по всем монетам, ищем подходящие по условиям
                for coin in coins:
                    for chain in coin_chains:
                        # Проверяем:
                        # - валюта совпадает
                        # - не делистнута
                        # - включены ввод, вывод и торговля
                        if (
                            chain["currency"] == coin
                            and not chain["delisted"]
                            and not chain["withdraw_disabled"]
                            and not chain["withdraw_delayed"]
                            and not chain["deposit_disabled"]
                            and not chain["trade_disabled"]
                        ):
                            # Добавляем монету, если она прошла фильтрацию
                            coin_list_gateio.append(chain["currency"])

                # Формируем финальный словарь цен
                coin_dict_gateio_price = {}
                
                # Создаём директорию для сохранения, если её нет
                os.makedirs("data/price", exist_ok=True)

                # Собираем только цены для прошедших фильтр монет
                for coin in coin_list_gateio:
                    for pair in usdt_pairs:
                        if pair["currency_pair"] == coin + "_USDT":
                            coin_dict_gateio_price[coin + "/USDT"] = {
                                "last": float(pair["last"]),            # последняя сделка
                                "ask": float(pair["lowest_ask"]),       # текущая цена продажи
                                "bid": float(pair["highest_bid"])       # текущая цена покупки
                            }

                # Сохраняем результат в JSON
                with open("data/price/gateio_price.json", "w") as f:
                    json.dump(coin_dict_gateio_price, f)
