# ------------------------------------------
# Файл: utils.py (core/fees)
# Назначение: Асинхронное получение данных о комиссиях на ввод/вывод криптовалют
# с различных бирж, включая OKEX, Gate.io и другие, используя их API.
# ------------------------------------------
import asyncio  # для запуска асинхронных задач
import base64  # для кодирования подписи OKEX в base64
import hashlib  # для хеширования сообщений
import hmac  # для генерации HMAC-подписи
import datetime  # для получения UTC времени
import aiohttp  # асинхронные HTTP-запросы

# Импорт функции получения комиссии с Gate.io (отдельный sync API)
from core.fees.gateio import get_fee_gateio

# Импорт ключей для OKEX из .env
from config.secrets import OKEX_API_KEY, OKEX_SECRET, OKEX_PASSWORD

# Асинхронная функция получения комиссий с конкретной биржи
async def fetch_fees(exchange):
    fees = {}  # словарь для хранения комиссий по валютам
    try:
        # 🔹 Обработка OKEX (требует ручной подписи HMAC)
        if exchange.id == "okex":
            base_url = "https://www.okx.com"
            path = "/api/v5/asset/currencies"
            url = base_url + path

            # Создаём временную метку в ISO-формате
            timestamp = datetime.datetime.utcnow().isoformat("T", "seconds") + "Z"
            method = "GET"
            body = ""  # GET-запрос без тела

            # Формируем строку сообщения для подписи
            message = timestamp + method + path + body
            secret = exchange.secret.encode()  # секретный ключ из exchange
            signature = hmac.new(secret, message.encode(), hashlib.sha256).digest()
            sign_b64 = base64.b64encode(signature).decode()  # base64 подпись

            # Заголовки для OKEX API
            headers = {
                'OK-ACCESS-KEY': OKEX_API_KEY,
                'OK-ACCESS-SIGN': sign_b64,
                'OK-ACCESS-TIMESTAMP': timestamp,
                'OK-ACCESS-PASSPHRASE': OKEX_PASSWORD,
            }

            # Асинхронный GET-запрос
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    result = await response.json()

                    # Обрабатываем список валют
                    for item in result.get("data", []):
                        coin = item.get("ccy")  # тикер монеты (например BTC)
                        if not coin:
                            continue
                        fee_info = {
                            "info": {coin: item},
                            "networks": {}
                        }
                        # Обрабатываем комиссии по каждой сети монеты
                        for net in item.get("chains", []):
                            chain_name = net.get("chain")
                            if chain_name:
                                fee_info["networks"][chain_name] = {
                                    "withdraw": {
                                        "fee": float(net.get("minFee", 0.0))
                                    }
                                }
                        fees[coin] = fee_info

        # 🔹 Обработка Gate.io — оборачиваем sync API через run_in_executor
        elif exchange.id == "gateio":
            loop = asyncio.get_event_loop()
            fees = await loop.run_in_executor(None, get_fee_gateio)

        # 🔹 Универсальный случай для других бирж
        else:
            fees = await exchange.fetch_deposit_withdraw_fees()

        return fees

    except Exception as e:
        # Вывод ошибки в консоль
        print(f"[ERROR] Failed to fetch fees from {exchange.id}: {e}")
        raise
    finally:
        # Закрываем подключение к бирже
        await exchange.close()