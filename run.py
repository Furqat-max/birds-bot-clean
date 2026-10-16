import subprocess
import sys
import os

# 1. Django veb-serverini (Gunicorn) orqa fonda ishga tushirish
port = os.environ.get("PORT", "10000")
print(f"--> Gunicorn veb-server {port}-portda ishga tushmoqda...")
web_process = subprocess.Popen([
    sys.executable, "-m", "gunicorn", "core.wsgi:application",
    "--bind", f"0.0.0.0:{port}"
])

# 2. Telegram botni alohida jarayon sifatida to'xtovsiz ishga tushirish
print("--> Telegram bot ishga tushmoqda...")
bot_process = subprocess.Popen([
    sys.executable, "bot.py"
])

# Jarayonlar to'xtab qolmasligi uchun kutib turamiz
try:
    bot_process.wait()
    web_process.wait()
except KeyboardInterrupt:
    bot_process.terminate()
    web_process.terminate()
