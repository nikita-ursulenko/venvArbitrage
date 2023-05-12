import subprocess
import time

while True:
    # Указываем путь к интерпретатору Python и путь к файлу main.py
    cmd = ["python3", "Arbitrage/main.py"]

    # Запускаем процесс
    subprocess.run(cmd)

    # Ждем 1 минуту
    time.sleep(60)

