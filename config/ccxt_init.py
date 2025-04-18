# ------------------------------------------
# Файл: ccxt_init.py
# Назначение: содержит асинхронную инициализацию подключений к криптовалютным биржам
# с использованием API-ключей, полученных из файла конфигурации `secrets.py`.
# Этот модуль используется для взаимодействия с биржами через библиотеку ccxt
# (асинхронная версия), что позволяет получать данные, торговать и выполнять другие операции.
# ------------------------------------------

# Импортируем асинхронную версию библиотеки ccxt под именем ccxt.
# Эта библиотека предоставляет единый интерфейс для работы с разными криптобиржами.
import ccxt.async_support as ccxt

# Импортируем секретные API-ключи и пароли для подключения к биржам из отдельного файла.
# Эти ключи хранятся отдельно от основного кода для безопасности.
from config.secrets import (
    OKEX_API_KEY, OKEX_SECRET, OKEX_PASSWORD,
    GATEIO_API_KEY, GATEIO_SECRET,
    HUOBI_API_KEY, HUOBI_SECRET,
    MEXC_API_KEY, MEXC_SECRET
)

# Создаём объект биржи OKEX с использованием API-ключа, секрета и пароля.
# Эти параметры позволяют аутентифицировать доступ к аккаунту на бирже.
okex = ccxt.okex({
    'apiKey': OKEX_API_KEY,
    'secret': OKEX_SECRET,
    'password': OKEX_PASSWORD,
})

# Создаём объект биржи Gate.io — передаём ключ и секрет (пароль здесь не требуется).
gateio = ccxt.gateio({
    'apiKey': GATEIO_API_KEY,
    'secret': GATEIO_SECRET,
})

# Создаём объект биржи Huobi — также используется ключ и секрет.
huobi = ccxt.huobi({
    'apiKey': HUOBI_API_KEY,
    'secret': HUOBI_SECRET,
})

# Создаём объект биржи MEXC — аналогично.
mexc = ccxt.mexc({
    'apiKey': MEXC_API_KEY,
    'secret': MEXC_SECRET,
})