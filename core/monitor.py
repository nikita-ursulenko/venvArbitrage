# ------------------------------------------
# Файл: monitor.py (core)
# Назначение: Запускает основной скрипт main.py в отдельном потоке и отслеживает
# дату последнего обновления JSON-файла с результатами. При каждом запуске вызывает
# callback-функцию, передавая в неё отформатированное время последнего обновления.
# Используется для автоматического мониторинга данных.
# ------------------------------------------
import subprocess  # используется для запуска внешнего Python-скрипта (main.py)
import os  # модуль для работы с файловой системой
import threading  # позволяет запускать функцию в отдельном потоке
import time  # используется для задержки между итерациями мониторинга
from datetime import datetime  # для форматирования времени
import sys  # доступ к текущему исполняемому интерпретатору Python

# Определяем путь до main.py относительно текущего файла
main_py_path = os.path.join(os.path.dirname(__file__), 'main.py')

# Запускает main.py и при наличии JSON-файла вызывает callback с временем его обновления
def run_main_once(callback, main_py_path, json_path):
    try:
        # Запуск main.py с использованием текущего интерпретатора Python
        subprocess.run([sys.executable, main_py_path])

        # Проверяем, существует ли JSON-файл
        if os.path.exists(json_path):
            # Получаем время последнего изменения файла
            mtime = os.path.getmtime(json_path)
            formatted_time = datetime.fromtimestamp(mtime).strftime("%H:%M")
            # Передаём отформатированное время в callback
            callback(formatted_time)
    except Exception as e:
        print("Ошибка при запуске main.py:", e)

# Запускает бесконечный цикл, который повторно вызывает run_main_once каждую минуту
def start_monitoring(callback, main_py_path, json_path, interval=60):
    def loop():
        while True:
            # Запускаем выполнение main.py в отдельном потоке
            threading.Thread(target=run_main_once, args=(callback, main_py_path, json_path)).start()
            time.sleep(interval)  # Ждём заданный интервал перед следующей итерацией

    # Запускаем цикл в отдельном фоновом потоке (демон)
    threading.Thread(target=loop, daemon=True).start()
