# Arbitrage Crypto System

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

