def delete_keys(data):
    # ------------------------------------------
    # Функция: delete_keys
    # Назначение: удаляет из словаря data те записи, которые не удовлетворяют условиям:
    # если спред недостаточно превышает комиссию, или если процент вывода выше спреда,
    # но при этом спред выше комиссии * 1.3
    # ------------------------------------------
    
    keys_to_delete = []  # сюда сохраняем ключи, которые нужно удалить

    # Проходим по всем записям в словаре
    for key, value in data.items():
        if value is not None and isinstance(value, dict):  # фильтруем только словари
            ask_fee = value.get('ask_fee', {})  # получаем комиссии на вывод
            fee = 0  # по умолчанию комиссия равна нулю

            # Получаем первую найденную комиссию на вывод (из ask_fee)
            if ask_fee:
                for currency, details in ask_fee.items():
                    withdraw = details.get('withdraw', {})
                    if withdraw:
                        fee = withdraw.get('fee', 0)
                        break  # берём только первую подходящую комиссию

            spread_percent = value.get('spread_percent', 0)  # получаем текущий спред

            # Если спред меньше 130% от комиссии — удалим эту пару
            if spread_percent < fee * 1.3:
                keys_to_delete.append(key)

            # Дополнительная проверка — процент вывода (если он есть)
            if value.get('ask_withdraw_percent', 0):
                ask_withdraw_percent = value.get('ask_withdraw_percent', 0)
                ask_withdraw_percent = ask_withdraw_percent.replace("%", "")  # убираем символ %
                ask_withdraw_percent = float(ask_withdraw_percent)

                # Если процент вывода выше спреда, но сам спред превышает 130% комиссии — тоже удалим
                if ask_withdraw_percent > spread_percent:
                    if spread_percent > fee * 1.3:
                        keys_to_delete.append(key)

    # Удаляем все ключи, которые были помечены к удалению
    for key in keys_to_delete:
        del data[key]