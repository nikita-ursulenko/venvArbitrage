# ------------------------------------------
# Файл: gateio.py (core/fees)
# Назначение: Получение данных о фиксированных комиссиях на вывод средств (withdraw fees)
# с биржи Gate.io через их официальный API. Используется для сбора информации о комиссиях
# по каждому токену и сети. Запрос требует подписи, сгенерированной через HMAC.
# ------------------------------------------

import time  # для получения текущего времени (необходимо для подписи)
import hmac  # для создания HMAC-подписей
import hashlib  # для хеширования тела запроса
from config.secrets import ( 
    GATEIO_API_KEY, GATEIO_SECRET
)  # импортируем ключи из файла конфигурации

def get_fee_gateio():


    # 🔐 Генерация заголовков подписи для Gate.io API (по их документации)
    def gen_sign(method, url, query_string=None, payload_string=None):
        t = str(int(time.time()))  # временная метка (в секундах)
        m = hashlib.sha512()  # создаём объект хеширования SHA-512
        m.update((payload_string or "").encode('utf-8'))  # хешируем тело запроса (если оно есть)
        hashed_payload = m.hexdigest()  # получаем hex-строку хеша

        # Формируем строку по формату Gate.io: METHOD\nURL\nQUERY\nBODY_HASH\nTIMESTAMP
        s = '%s\n%s\n%s\n%s\n%s' % (method.upper(), url, query_string or "", hashed_payload, t)

        # Генерация подписи HMAC-SHA512 на основе строки `s`
        sign = hmac.new(GATEIO_SECRET.encode('utf-8'), s.encode('utf-8'), hashlib.sha512).hexdigest()

        # Возвращаем словарь заголовков для авторизации
        return {
            'KEY': GATEIO_API_KEY,
            'Timestamp': t,
            'SIGN': sign
        }

    # 📡 Основные параметры запроса
    host = "https://api.gateio.ws"
    prefix = "/api/v4"
    common_headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

    # 📍 Конечная точка API для получения информации о комиссиях на вывод
    url = '/wallet/withdraw_status'

    # 🔐 Генерация заголовков подписи для запроса
    sign_headers = gen_sign('GET', prefix + url, "", "")
    headers = {**common_headers, **sign_headers}  # объединяем заголовки

    import requests
    try:
        # 🚀 Выполнение GET-запроса к API Gate.io
        response = requests.get(host + prefix + url, headers=headers)
        response.raise_for_status()  # выброс исключения при коде ответа 4xx/5xx
        result = response.json()  # преобразуем JSON-ответ в Python-словарь

        fees = {}  # здесь будут храниться комиссии по каждому токену

        for item in result:
            currency = item.get("currency")  # токен, например BTC, ETH
            if not currency:
                continue

            networks = {}  # словарь с комиссиями по сетям (например, ERC20, TRC20)
            for chain, fee_str in item.get("withdraw_fix_on_chains", {}).items():
                try:
                    fee_val = float(fee_str)  # пробуем привести к числу
                    networks[chain] = {
                        "withdraw": {
                            "fee": fee_val  # сохраняем комиссию в виде числа
                        }
                    }
                except Exception:
                    continue  # если не получилось — пропускаем

            # Сохраняем инфу по токену
            fees[currency] = {
                "info": item,  # оригинальный объект API (на всякий случай)
                "networks": networks  # комиссии по сетям
            }

        return fees  # ✅ Возвращаем результат
    except Exception as e:
        # Если ошибка — выводим её
        print(f"[ERROR] Failed to manually fetch Gate.io withdraw status: {e}")
        return {}
    finally:
        # В любом случае пишем, что завершено
        print("Manual fetch completed.")