import importlib
import asyncio

EXCHANGES = ['bybit', 'gateio', 'huobi', 'kucoin', 'mexc', 'okex']

async def fetch_all_prices():
    tasks = []
    for name in EXCHANGES:
        module = importlib.import_module(f'core.prices.{name}')
        task = getattr(module, f'{name}_price')()
        tasks.append(task)
    await asyncio.gather(*tasks)