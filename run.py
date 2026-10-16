import subprocess
import os
import sys

# 1. Django veb-serverini (Gunicorn) orqa fonda ishga tushiramiz
port = os.environ.get("PORT", "10000")
web_process = subprocess.Popen([
    sys.executable, "-m", "gunicorn", "core.wsgi:application", 
    "--bind", f"0.0.0.0:{port}"
])

# 2. Telegram botni asosiy jarayon sifatida yurgizamiz
try:
    import bot
except Exception as e:
    print(f"Botda xatolik: {e}")
