# ------------------------------------------
# Файл: secrets.py
# Назначение: безопасная загрузка конфиденциальных API-ключей и паролей
# из файла окружения `.env` с использованием библиотеки dotenv.
# Эти ключи используются для подключения к различным криптобиржам.
# ------------------------------------------

# Импорт стандартного модуля os для доступа к переменным окружения
import os

# Импорт функции load_dotenv, которая загружает переменные окружения из файла .env
from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла, если он существует
load_dotenv()

# Получение API-ключа, секрета и пароля для биржи OKEX из переменных окружения.
# Если переменная отсутствует, будет возвращена пустая строка.
OKEX_API_KEY = os.getenv("OKEX_API_KEY", "")
OKEX_SECRET = os.getenv("OKEX_API_SECRET", "")
OKEX_PASSWORD = os.getenv("OKEX_PASSWORD", "")

# Получение API-ключа и секрета для биржи Gate.io
GATEIO_API_KEY = os.getenv("GATEIO_API_KEY", "")
GATEIO_SECRET = os.getenv("GATEIO_API_SECRET", "")

# Получение API-ключа и секрета для биржи Huobi
HUOBI_API_KEY = os.getenv("HUOBI_API_KEY", "")
HUOBI_SECRET = os.getenv("HUOBI_API_SECRET", "")

# Получение API-ключа и секрета для биржи MEXC
MEXC_API_KEY = os.getenv("MEXC_API_KEY", "")
MEXC_SECRET = os.getenv("MEXC_API_SECRET", "")

# Получение API-ключа и секрета для биржи KuCoin
KUCOIN_API_KEY = os.getenv("KUCOIN_API_KEY", "")
KUCOIN_SECRET = os.getenv("KUCOIN_API_SECRET", "")
KUCOIN_PASSWORD = os.getenv("KUCOIN_PASSWORD", "")