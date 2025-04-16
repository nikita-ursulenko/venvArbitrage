# ------------------------------------------
# Файл: launch.py (interface)
# Назначение: Основной графический интерфейс программы арбитража.
# ------------------------------------------

# Импорт системных модулей
import sys
import os

# Добавляем путь к родительской директории в sys.path, чтобы можно было импортировать модули из core и interface
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Импорт внешних библиотек
import json  # для работы с файлами .json
import subprocess  # не используется в текущей версии, но может быть для запуска внешних процессов
import time  # используется в анимации и задержках
import ccxt  # библиотека для взаимодействия с API криптобирж (не используется напрямую в этом файле)
import tkinter as tk  # основной GUI toolkit
from tkinter import ttk, scrolledtext  # виджеты из tkinter
import threading  # для запуска фоновых задач
from datetime import datetime  # для метки времени

# Импорт кастомных функций
from core.monitor import start_monitoring  # отслеживает обновление main.json
import concurrent.futures  # для запуска анализа в пуле потоков
from core.profit.calculate import process_item  # логика расчета прибыли по паре
from interface.render import format_result_as_text_widget_links  # форматирует результат как текст с кнопками

# Загружаем исходный JSON с монетами и биржами для интерфейса (один раз)
with open('data/main.json', 'r') as f:
    data = json.load(f)

# Не используется, но оставлен как пример
def process_data(data):
    # Функция для обработки данных с использованием пула потоков
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Создаем задачи для каждого элемента данных
        futures = [executor.submit(process_item, key, value) for key, value in data.items()]
        # Обрабатываем результаты по мере их завершения
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                print(result)

# -----------------------------------------------------------------------------
# Основная функция интерфейса
# -----------------------------------------------------------------------------
def run_interface():
    # Создаём временное окно-загрузчик
    splash = tk.Tk()
    splash.attributes("-topmost", True)  # Устанавливаем окно поверх всех других окон
    splash.title("Загрузка...")  # Заголовок окна
    splash.geometry("300x100")  # Устанавливаем размеры окна
    splash_label = ttk.Label(splash, text="⏳ Загрузка...", font=("Arial", 14, "italic"))  # Метка загрузки
    splash_label.pack(expand=True)  # Размещаем метку в центре окна

    splash.protocol("WM_DELETE_WINDOW", lambda: None)  # Блокируем закрытие splash окна вручную
    is_animating = True  # Флаг для анимации статуса
    first_data_ready = False  # Определяет, был ли выполнен хотя бы один update
    splash_active = True  # Флаг активности splash окна
    after_id = None  # Идентификатор отложенного вызова .after()

    # Функция анимации текста "Загрузка..."
    def splash_animation():
        dots = ["", ".", "..", "..."]  # Различные состояния анимации
        i = 0  # Индекс текущего состояния

        def update_label():
            nonlocal i, after_id  # Используем внешние переменные
            try:
                if splash_active and splash.winfo_exists():  # Проверяем, активно ли окно
                    splash_label.config(text=f"⏳ Загрузка{dots[i % 4]}")  # Обновляем текст метки
                    i += 1  # Переходим к следующему состоянию
                    after_id = splash.after(500, update_label)  # Запускаем следующий вызов через 500 мс
            except tk.TclError:
                return  # Игнорируем ошибки, если окно закрыто

        update_label()  # Запускаем обновление метки

    splash_animation()  # Запускаем анимацию загрузки

    # Фоновая анимация статуса "Анализ..."
    def animate_analysis_status():
        dots = ["", ".", "..", "..."]  # Различные состояния анимации
        i = 0  # Индекс текущего состояния
        while is_animating:  # Пока анимация активна
            status_label.config(text=f"🔄 Анализ{dots[i % 4]}")  # Обновляем текст статуса
            i += 1  # Переходим к следующему состоянию
            time.sleep(0.5)  # Задержка для анимации

    analysis_thread = None  # Хранит поток анализа

    def on_run():
        nonlocal analysis_thread  # Используем внешнюю переменную для хранения потока
        def task():
            nonlocal is_animating  # Используем внешнюю переменную для флага анимации
            is_animating = True  # Устанавливаем флаг анимации
            threading.Thread(target=animate_analysis_status, daemon=True).start()  # Запускаем анимацию в фоновом потоке
            run_button.config(state="disabled")  # Блокируем кнопку запуска
            results_text.delete('1.0', tk.END)  # Очищаем вывод результатов
            try:
                amount_usdt = float(amount_entry.get())  # Получаем сумму капитала из поля ввода
                with open('data/main.json', 'r') as f:
                    local_data = json.load(f)  # Загружаем данные из JSON
                with concurrent.futures.ThreadPoolExecutor() as executor:  # Создаем пул потоков
                    # Создаем задачи для каждого элемента данных с учетом суммы капитала
                    futures = [executor.submit(process_item, key, value, amount_usdt) for key, value in local_data.items()]
                    # Обрабатываем результаты по мере их завершения
                    for future in concurrent.futures.as_completed(futures):
                        if getattr(threading.current_thread(), "stopped", False):  # Проверяем, остановлен ли поток
                            break
                        result = future.result()  # Получаем результат выполнения задачи
                        if result:  # Если результат не пустой
                            # Обновляем текстовый виджет с результатами в основном потоке интерфейса
                            results_text.after(0, lambda r=result: (
                                format_result_as_text_widget_links(results_text, r),  # Форматируем результат
                                results_text.see(tk.END)  # Прокручиваем текстовое поле к последнему результату
                            ))
            except Exception as e:
                results_text.insert(tk.END, f"Ошибка: {str(e)}")  # Обрабатываем ошибки и выводим их
            finally:
                is_animating = False  # Сбрасываем флаг анимации
                status_label.config(text="✅ Анализ завершён")  # Обновляем статус
                analysis_thread = None  # Сбрасываем поток анализа
            run_button.config(state="normal")  # Разблокируем кнопку запуска

        analysis_thread = threading.Thread(target=task)  # Создаем новый поток для задачи
        setattr(analysis_thread, "stopped", False)  # Устанавливаем флаг остановки для потока
        analysis_thread.start()  # Запускаем поток

    def on_clear():
        nonlocal analysis_thread, is_animating  # Используем внешние переменные
        results_text.delete('1.0', tk.END)  # Очищаем вывод результатов
        if analysis_thread and analysis_thread.is_alive():  # Если анализ еще идет
            is_animating = False  # Останавливаем анимацию
            setattr(analysis_thread, "stopped", True)  # Устанавливаем флаг остановки для потока
            analysis_thread = None  # Сбрасываем поток анализа
            run_button.config(state="normal")  # Разблокируем кнопку запуска
            status_label.config(text="🛑 Анализ прерван")  # Обновляем статус
        else:
            status_label.config(text="🧹 Чат очищен")  # Обновляем статус при очистке

    # Основное окно приложения
    window = tk.Tk()  # Создаем главное окно приложения
    window.withdraw()  # Скрываем его до завершения загрузки
    window.title("Arbitrage Checker")  # Заголовок главного окна
    window.geometry("920x600")  # Устанавливаем размеры главного окна

    frame = ttk.Frame(window, padding=10)  # Создаем фрейм для размещения элементов интерфейса
    frame.pack(fill=tk.BOTH, expand=True)  # Заполняем доступное пространство

    # Панель с кнопками и вводом суммы
    control_panel = ttk.Frame(frame)  # Создаем фрейм для панели управления
    control_panel.pack(fill=tk.X, pady=5)  # Устанавливаем заполнение по оси X

    amount_label = ttk.Label(control_panel, text="Капитал $:")  # Метка для поля ввода капитала
    amount_label.pack(side=tk.LEFT, padx=(0, 5))  # Размещаем метку слева
    amount_entry = ttk.Entry(control_panel)  # Поле ввода для капитала
    amount_entry.insert(0, "95")  # Значение по умолчанию
    amount_entry.pack(side=tk.LEFT, padx=(0, 10))  # Размещаем поле ввода слева

    run_button = ttk.Button(control_panel, text="Запустить анализ", command=lambda: threading.Thread(target=on_run).start())  # Кнопка для запуска анализа
    run_button.pack(side=tk.LEFT, padx=(0, 5))  # Размещаем кнопку слева

    clear_button = ttk.Button(control_panel, text="Очистить", command=on_clear)  # Кнопка для очистки результатов
    clear_button.pack(side=tk.LEFT, padx=(0, 10))  # Размещаем кнопку слева

    # Поле с результатами и прокруткой
    results_text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, width=100, height=30)  # Поле для вывода результатов
    results_text.pack(pady=10, fill=tk.BOTH, expand=True)  # Размещаем поле с прокруткой

    timestamp_label = ttk.Label(control_panel, text="Последнее обновление: -")  # Метка для времени последнего обновления
    timestamp_label.pack(side=tk.LEFT, padx=(0, 10))  # Размещаем метку слева

    status_label = ttk.Label(control_panel, text="⏳ Загрузка...", font=("Arial", 12, "italic"))  # Метка для статуса
    status_label.pack(side=tk.LEFT)  # Размещаем метку слева

    # Функция обновления UI при поступлении времени из мониторинга
    def update_ui_callback(formatted_time):
        nonlocal first_data_ready, is_animating, splash_active, after_id  # Используем внешние переменные
        if after_id is not None:  # Если есть отложенный вызов
            try:
                splash.after_cancel(after_id)  # Отменяем отложенный вызов
            except Exception:
                pass  # Игнорируем ошибки
        timestamp_label.config(text=f"Последнее обновление: {formatted_time}")  # Обновляем метку времени
        if not first_data_ready:  # Если это первое обновление
            splash_active = False  # Устанавливаем флаг активности в False
            status_label.config(text="✅ Готов к запуску")  # Обновляем статус
            run_button.config(state="normal")  # Разблокируем кнопку запуска
            first_data_ready = True  # Устанавливаем флаг, что данные готовы
            splash.destroy()  # Закрываем окно загрузки
            window.deiconify()  # Показываем главное окно

    # Запускаем мониторинг main.json
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    main_py_path = os.path.join(base_dir, "main.py")
    json_path = os.path.join(base_dir, "data", "main.json")

    start_monitoring(lambda time: window.after(0, lambda: update_ui_callback(time)),
                     main_py_path=main_py_path,
                     json_path=json_path)  # Путь к main.json

    window.mainloop()  # Запускаем основной цикл приложения

# Точка входа
if __name__ == "__main__":
    run_interface()  # Запускаем интерфейс при запуске файла напрямую
