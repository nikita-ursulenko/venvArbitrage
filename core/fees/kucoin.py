import base64
import hashlib
import hmac
import time
import requests
from config.secrets import KUCOIN_API_KEY, KUCOIN_SECRET, KUCOIN_PASSWORD
def get_fee_kucoin(currency, value):

    # создание метки времени в миллисекундах
    nonce = str(int(time.time() * 1000))

    # формирование подписи запроса
    message = f'{nonce}GET/api/v1/withdrawals/quotas?currency={currency}'
    signature = base64.b64encode(hmac.new(KUCOIN_SECRET.encode(), message.encode(), hashlib.sha256).digest()).decode()

    # формирование заголовков запроса
    headers = {
        'KC-API-KEY': KUCOIN_API_KEY,
        'KC-API-SIGN': signature,
        'KC-API-TIMESTAMP': nonce,
        'KC-API-PASSPHRASE': KUCOIN_PASSWORD
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
  