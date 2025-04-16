# ------------------------------------------
# Файл: updater.py (core)
# Назначение:
# Данный модуль обрабатывает файл spreads.json, в котором собраны потенциальные арбитражные сделки.
# Он проверяет, доступны ли монеты для вывода и ввода на соответствующих биржах, используя
# данные комиссий (fees) с каждой биржи, и рассчитывает стоимость вывода в долларах.
# При невозможности совершения вывода или ввода монета исключается из дальнейшей обработки.
# Результатом является словарь с обновлёнными данными по комиссиям и фильтрацией невалидных монет.
# ------------------------------------------

import json
import time

from core.fees.kucoin import get_fee_kucoin


def update_fees(okex_fees, gateio_fees, huobi_fees, mexc_fees):
    # Загружаем данные по арбитражным возможностям, полученные после расчёта спреда
    with open("data/spread/spreads.json", "r") as f:
        data = json.load(f)
    
    # Обходим каждую арбитражную запись из spreads.json
    # Для каждой монеты проверяем комиссии на вывод (ask_fee) и ввод (bid_fee) с бирж
    keys_to_delete = []
    for key, value in data.items():
        # --- Блок обработки биржи OKEX для ASK ---
        # Проверка: монета должна выводиться с биржи OKEX, если она указана как ask_name (покупка)
        # Проверяем комиссии на вывод, актуальность вывода, пересчитываем в USD
        if "OKEX" in value["ask_name"]:
            # Получаем тикер монеты из текущей записи
            symbol = value["symbol"]
            # Извлекаем комиссионные данные для этой монеты из словаря fees соответствующей биржи
            fees = okex_fees.get(symbol)
            info = fees["info"][symbol]
            # Проверка доступности операций (вывод, ввод, торговля и т.д.) по монете на бирже
            # Есть валидность на доступность вывода
            # FILTER
            if info["canInternal"] and info["canWd"]:
                networks = fees["networks"]
                # Переводим комиссию из единиц монеты в долларовый эквивалент (ask * fee)
                for network in networks.keys():
                    networks[network]["withdraw"]["fee"] = value["ask"] * float(networks[network]["withdraw"]["fee"])
                # Сохраняем рассчитанные данные о комиссиях в поле ask_fee (или bid_fee)
                value["ask_fee"] = networks
                # Если процент не предоставляется биржей — устанавливаем значение по умолчанию
                value["ask_withdraw_percent"] = 0
            else:
                # Монета не проходит условия (вывод/ввод запрещён или комиссия невалидна) — исключаем
                keys_to_delete.append(key)
        # --- Блок обработки биржи OKEX для BID ---
        # Проверка: монета должна приниматься на бирже OKEX, если она указана как bid_name (продажа)
        # Проверяем возможность пополнения, сохраняем список сетей
        if "OKEX" in value["bid_name"]:
            # Получаем тикер монеты из текущей записи
            symbol = value["symbol"]
            # Извлекаем комиссионные данные для этой монеты из словаря fees соответствующей биржи
            fees = okex_fees.get(symbol)
            if fees is None or "info" not in fees or symbol not in fees["info"]:
                print(f"[ERROR] Missing info for OKEX symbol={symbol}, fees={fees}")
                # Монета не проходит условия (вывод/ввод запрещён или комиссия невалидна) — исключаем
                keys_to_delete.append(key)
                continue
            info = fees["info"][symbol]
            # Проверка доступности операций (вывод, ввод, торговля и т.д.) по монете на бирже
            # Если можно торговать и пополнять
            if info["canInternal"] and info["canDep"]:
                networks = fees["networks"]
                value["bid_fee"] = list(networks.keys())
            else:
                # Монета не проходит условия (вывод/ввод запрещён или комиссия невалидна) — исключаем
                keys_to_delete.append(key)

        # --- Блок обработки биржи Gateio для ASK ---
        # Проверка: монета должна выводиться с биржи Gateio, если она указана как ask_name (покупка)
        # Проверяем комиссии на вывод, актуальность вывода, пересчитываем в USD
        if "Gateio" in value["ask_name"]:
            # Получаем тикер монеты из текущей записи
            symbol = value["symbol"]
            # Извлекаем комиссионные данные для этой монеты из словаря fees соответствующей биржи
            fees = gateio_fees.get(symbol)
            if not fees or "info" not in fees:
                print(f"[ERROR] Missing or invalid fee data for {symbol}, fees={fees}")
                # Монета не проходит условия (вывод/ввод запрещён или комиссия невалидна) — исключаем
                keys_to_delete.append(key)
                continue
            info = fees["info"]
            # Проверка доступности операций (вывод, ввод, торговля и т.д.) по монете на бирже
            # Валидноть присутсвует в gateio_price(), выводим только актуальные монеты 
            # FILTER
            # Если дневной лимит больше 0 то выполняем дальше
            if float(info["withdraw_day_limit"]) > 0:
                # Обьявляем переменную 
                networks = fees["networks"]
                # Перебираем ключи переменной
                # Переводим комиссию из единиц монеты в долларовый эквивалент (ask * fee)
                for network in networks.keys():
                    networks[network]["withdraw"]["fee"] = value["ask"] * float(networks[network]["withdraw"]["fee"])
                # Сохраняем рассчитанные данные о комиссиях в поле ask_fee (или bid_fee)
                value["ask_fee"] = networks
                # Если процент не пустой 
                if info["withdraw_percent"] != None:
                    # Создаем ключ и передаем значение 
                    value["ask_withdraw_percent"] = info["withdraw_percent"]
                # Если процент не предоставляется биржей — устанавливаем значение по умолчанию
                else: value["ask_withdraw_percent"] = 0
            # Значит не можем вывести
            else: value["ask_fee"] = None
        # --- Блок обработки биржи Gateio для BID ---
        # Проверка: монета должна приниматься на бирже Gateio, если она указана как bid_name (продажа)
        # Проверяем возможность пополнения, сохраняем список сетей
        if "Gateio" in value["bid_name"]:
            # Получаем тикер монеты из текущей записи
            symbol = value["symbol"]
            # Извлекаем комиссионные данные для этой монеты из словаря fees соответствующей биржи
            fees = gateio_fees.get(symbol)
            if fees:
                info = fees["info"]
                # Проверка доступности операций (вывод, ввод, торговля и т.д.) по монете на бирже
                if float(info["withdraw_day_limit"]) > 0:
                    networks = fees["networks"]
                    value["bid_fee"] = list(networks.keys())
            else: value["bid_fee"] = None
            
        # --- Блок обработки биржи Huobi для ASK ---
        # Проверка: монета должна выводиться с биржи Huobi, если она указана как ask_name (покупка)
        # Проверяем комиссии на вывод, актуальность вывода, пересчитываем в USD
        if "Huobi" in value["ask_name"]:
            # Получаем тикер монеты из текущей записи
            symbol = value["symbol"]
            # Извлекаем комиссионные данные для этой монеты из словаря fees соответствующей биржи
            fees = huobi_fees.get(symbol)
            if fees is not None:
                # Комиссия сетей
                chains = fees["info"].get("chains")
                if chains is not None:
                    networks = {}
                    for chain in chains:
                        # Если есть название то присваиваем 
                        if "baseChain" in chain:
                            network_name = chain["baseChain"]
                        # Иначе присваиваем другое имя 
                        else: network_name = chain["displayName"]
                        # Проверка доступности операций (вывод, ввод, торговля и т.д.) по монете на бирже
                        # Есть валидность на доступность вывода 
                        # FILTER
                        if chain["withdrawStatus"] != "prohibited":
                            withdraw = {}
                            fee = {}
                            # Переводим комиссию из единиц монеты в долларовый эквивалент (ask * fee)
                            if "transactFeeRateWithdraw" in chain:
                                fee_with = float(chain["transactFeeRateWithdraw"])
                            else: fee_with = float(chain["transactFeeWithdraw"])
                            fee["fee"] = round(fee_with * value["ask"], 1)
                            withdraw["withdraw"] = fee
                            networks[network_name] = withdraw
                        else:
                            # Монета не проходит условия (вывод/ввод запрещён или комиссия невалидна) — исключаем
                            keys_to_delete.append(key)

                    # Если процент не предоставляется биржей — устанавливаем значение по умолчанию
                    value["ask_withdraw_percent"] = 0
                else:
                    value["ask_fee"] = None
        # --- Блок обработки биржи Huobi для BID ---
        # Проверка: монета должна приниматься на бирже Huobi, если она указана как bid_name (продажа)
        # Проверяем возможность пополнения, сохраняем список сетей
        if "Huobi" in value["bid_name"]:
            # Получаем тикер монеты из текущей записи
            symbol = value["symbol"]
            # Извлекаем комиссионные данные для этой монеты из словаря fees соответствующей биржи
            fees = huobi_fees.get(symbol)
            if fees is not None:
                chains = fees["info"].get("chains")
                if chains is not None:
                    networks = {}
                    for chain in chains:
                        if "baseChain" in chain:
                            network_name = chain["baseChain"]
                        else: network_name = chain["displayName"]
                        networks = fees["networks"]
                        # Проверка доступности операций (вывод, ввод, торговля и т.д.) по монете на бирже
                        if chain["depositStatus"] == "prohibited":
                            # Монета не проходит условия (вывод/ввод запрещён или комиссия невалидна) — исключаем
                            keys_to_delete.append(key)
                    value["bid_fee"] = list(networks.keys())
                else:
                    value["bid_fee"] = None

        # --- Блок обработки биржи MEXC для ASK ---
        # Проверка: монета должна выводиться с биржи MEXC, если она указана как ask_name (покупка)
        # Проверяем комиссии на вывод, актуальность вывода, пересчитываем в USD
        if "MEXC" in value["ask_name"]:
            # Получаем тикер монеты из текущей записи
            symbol = value["symbol"]
            # Извлекаем комиссионные данные для этой монеты из словаря fees соответствующей биржи
            fees = mexc_fees.get(symbol)
            ask = value["ask"]
            if fees is not None:
                if fees is None or "info" not in fees or "networkList" not in fees["info"]:
                    print(f"[SKIP][MEXC ASK] {symbol} — fees missing or invalid: {fees}")
                    continue
                ask_fee = {}
                for network in fees["info"]["networkList"]:
                    if network.get("withdrawEnable") is True:
                        network_name = network.get("network")
                        network_fee = network.get("withdrawFee")
                        if ask is None or not isinstance(ask, (int, float)) or network_fee is None:
                            print(f"[SKIP][MEXC ASK] {symbol} — invalid ask or fee: ask={ask}, fee={network_fee}")
                            continue
                        try:
                            # Переводим комиссию из единиц монеты в долларовый эквивалент (ask * fee)
                            ask_fee[network_name] = {
                                "withdraw": {
                                    "fee": round(float(network_fee) * ask, 2)
                                }
                            }
                        except Exception as e:
                            print(f"[ERROR][MEXC ASK] Failed to calculate fee for {symbol}, network={network_name}, fee={network_fee}, error: {e}")
                            continue
                    else:
                        # Монета не проходит условия (вывод/ввод запрещён или комиссия невалидна) — исключаем
                        keys_to_delete.append(key)
                if ask_fee:
                    # Сохраняем рассчитанные данные о комиссиях в поле ask_fee (или bid_fee)
                    value["ask_fee"] = ask_fee
                    value["ask_withdraw_percent"] = None
                else:
                    value["ask_fee"] = None
        # --- Блок обработки биржи MEXC для BID ---
        # Проверка: монета должна приниматься на бирже MEXC, если она указана как bid_name (продажа)
        # Проверяем возможность пополнения, сохраняем список сетей
        if "MEXC" in value["bid_name"]:
            # Получаем тикер монеты из текущей записи
            symbol = value["symbol"]
            # Извлекаем комиссионные данные для этой монеты из словаря fees соответствующей биржи
            fees = mexc_fees.get(symbol)
            if fees is not None:
                bid_fee = {}
                for network in fees["info"]["networkList"]:
                    if network.get("depositEnable") is True:
                        network_name = network.get("network")
                        bid_fee[network_name] = {}
                    else:
                        # Монета не проходит условия (вывод/ввод запрещён или комиссия невалидна) — исключаем
                        keys_to_delete.append(key)
                if bid_fee:
                    value["bid_fee"] = list(bid_fee.keys())
                else:
                    value["bid_fee"] = None

        # --- Блок обработки биржи KuCoin для ASK ---
        # Проверка: монета должна выводиться с биржи KuCoin, если она указана как ask_name (покупка)
        # Проверяем комиссии на вывод, актуальность вывода, пересчитываем в USD
        if "KuCoin" in value["ask_name"]:
            # Получаем тикер монеты из текущей записи
            symbol = value["symbol"]
            ask = value["ask"]
            withdrawal_limits = get_fee_kucoin(symbol, ask)
            if "error" in withdrawal_limits:
                print(f"Error: {withdrawal_limits['error']}")
                continue
            # Сохраняем рассчитанные данные о комиссиях в поле ask_fee (или bid_fee)
            value["ask_fee"] = withdrawal_limits
            time.sleep(0.6)
        # --- Блок обработки биржи KuCoin для BID ---
        # Проверка: монета должна приниматься на бирже KuCoin, если она указана как bid_name (продажа)
        # Проверяем возможность пополнения, сохраняем список сетей
        if "KuCoin" in value["bid_name"]:
            # Получаем тикер монеты из текущей записи
            symbol = value["symbol"]
            bid = value["bid"]
            withdrawal_limits = get_fee_kucoin(symbol, bid)
            if "error" in withdrawal_limits:
                print(f"Error: {withdrawal_limits['error']}")
                continue
            # Сохраняем рассчитанные данные о комиссиях в поле ask_fee (или bid_fee)
            value["bid_fee"] = withdrawal_limits 
            time.sleep(0.6)
    
    # Удаляем все монеты, которые были помечены как невалидные — по причине недоступности ввода/вывода
    for key in list(set(keys_to_delete)):
        del data[key]
    return data