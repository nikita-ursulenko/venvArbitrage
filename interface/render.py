# ------------------------------------------
# Файл: render.py (interface)
# Назначение: Отвечает за форматирование текстового результата анализа
# и вставку в виджет с поддержкой интерактивных кнопок (ссылок).
# Ссылки (http...) заменяются на кнопки с надписями: "Спот", "Вывод", "Депозит".
# ------------------------------------------
import tkinter as tk
from tkinter import ttk

# Функция принимает текстовый виджет и строку результата.
# Для каждой строки:
# - если она URL — вставляется кнопка с соответствующей меткой
# - иначе — текст вставляется построчно
# Каждая кнопка открывает ссылку в браузере.
def format_result_as_text_widget_links(text_widget, raw_text):
        text_widget.insert(tk.END, "\n")
        for line in raw_text.strip().split("\n"):
            # Проверяем, является ли строка ссылкой
            if line.startswith("http"):
                # Присваиваем метку кнопке в зависимости от содержания URL
                if "withdraw" in line:
                    label = "Вывод"
                elif "trade" in line or "exchange" in line:
                    label = "Спот"
                elif "deposit" in line:
                    label = "Депозит"
                else:
                    label = "Ссылка"

                # Определяем обработчик нажатия — открывает ссылку в браузере
                def callback(url=line):
                    import webbrowser
                    webbrowser.open(url)

                # Создаём кнопку с меткой и действием
                button = ttk.Button(text_widget, text=label, command=callback)
                # Вставляем кнопку в текстовый виджет
                text_widget.window_create(tk.END, window=button)
                text_widget.insert(tk.END, " ")
            else:
                # Вставляем обычную текстовую строку, если она не является ссылкой
                text_widget.insert(tk.END, line + "\n")
        text_widget.insert(tk.END, "\n")