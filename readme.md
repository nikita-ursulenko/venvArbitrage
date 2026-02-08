# Arbitrage Crypto System

<div align="center">
  <div style="display:flex; justify-content:center; gap:5px; flex-wrap:wrap; margin: 10px 0;">
    <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"></a>
    <a href="https://github.com/ccxt/ccxt"><img src="https://img.shields.io/badge/ccxt-000000?style=for-the-badge&logo=bitcoin&logoColor=white" alt="ccxt"></a>
    <a href="https://docs.python.org/3/library/asyncio.html"><img src="https://img.shields.io/badge/Asyncio-00599C?style=for-the-badge&logo=python&logoColor=white" alt="Asyncio"></a>
    <a href="https://docs.aiohttp.org/"><img src="https://img.shields.io/badge/aiohttp-2C5BB4?style=for-the-badge&logo=python&logoColor=white" alt="aiohttp"></a>
    <a href="https://docs.python.org/3/library/tkinter.html"><img src="https://img.shields.io/badge/Tkinter-2C2D72?style=for-the-badge&logo=python&logoColor=white" alt="Tkinter"></a>
    <a href="https://web3py.readthedocs.io/"><img src="https://img.shields.io/badge/Web3.py-F16822?style=for-the-badge&logo=ethereum&logoColor=white" alt="Web3.py"></a>
  </div>
</div>

📈 **Описание проекта**

Система автоматического поиска арбитражных возможностей между криптовалютными биржами с учётом комиссий, глубины стакана и динамического интерфейса.

Разработано на Python 3.11 с использованием:
- `ccxt` для работы с API криптобирж
- `asyncio`, `aiohttp` и `threading` для высокой производительности
- `tkinter` для интерфейса
- `dotenv` и `.env` для хранения API-ключей
- `JSON` — формат хранения промежуточных данных

---

## 🧠 Возможности

- Получение цен с популярных бирж (Bybit, Gateio, OKEX, KuCoin, MEXC, Huobi)
- Анализ спреда между биржами
- Учет комиссии на ввод/вывод
- Интерфейс с кнопками, статусом, автопрокруткой и ссылками на биржи
- Асинхронная и многопоточная обработка большого объема данных

---

## 🚀 Установка и запуск

### 1. Клонируйте репозиторий:
```bash
git clone https://github.com/nikita-ursulenko/venvArbitrage.git
cd venvArbitrage
```

### 2. Создайте и активируйте виртуальное окружение:
```bash
python3 -m venv .venv
source .venv/bin/activate  # для Linux/Mac
.venv\Scripts\activate   # для Windows
```

### 3. Установите зависимости:
```bash
pip install -r requirements.txt
```

### 4. Настройте файл `.env`

Создайте `.env` файл в корне и добавьте туда:

```
OKEX_API_KEY=...
OKEX_API_SECRET=...
OKEX_PASSWORD=...

GATEIO_API_KEY=...
GATEIO_API_SECRET=...

HUOBI_API_KEY=...
HUOBI_API_SECRET=...

MEXC_API_KEY=...
MEXC_API_SECRET=...

KUCOIN_API_KEY=...
KUCOIN_SECRET=...
KUCOIN_PASSPHRASE=...
```

### 5. Запуск интерфейса:
```bash
python interface/launch.py
```

---

## 📁 Структура проекта

```
core/               # Логика: комиссии, обновления, мониторинг, анализ
config/             # Настройки и подключение API
interface/          # Графический интерфейс (tkinter)
data/               # Промежуточные данные JSON
main.py             # Скрипт обновления main.json
```

---

## ⚠️ Важно

- Работайте только с собственными ключами от бирж

---

## 👨‍💻 Автор
Ursulenco Nichita

---

