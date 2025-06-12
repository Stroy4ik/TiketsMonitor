import threading
import subprocess


def run_bot():
    subprocess.run(["python3", "bot.py"])


def run_monitor():
    subprocess.run(["python3", "monitor.py"])


threading.Thread(target=run_bot).start()
threading.Thread(target=run_monitor).start()
