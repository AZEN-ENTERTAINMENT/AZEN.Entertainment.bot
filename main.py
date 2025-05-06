from flask import Flask, jsonify
import psutil
import os
import time
import logging

# تنظیمات لاگینگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logger = logging.getLogger("main_server")

app = Flask(__name__)

# پیکربندی
BOT_PROCESS_NAME = "bot.py"
WATCHDOG_PROCESS_NAME = "watchdog.py"
start_time = time.time()

def is_process_running(process_name):
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
            if process_name in cmdline:
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return False

def get_bot_status():
    return "running" if is_process_running(BOT_PROCESS_NAME) else "stopped"

def get_watchdog_status():
    return "running" if is_process_running(WATCHDOG_PROCESS_NAME) else "stopped"

def get_uptime():
    return round(time.time() - start_time, 2)

@app.route('/')
def home():
    bot_status = get_bot_status()
    watchdog_status = get_watchdog_status()
    cpu_percent = psutil.cpu_percent()
    memory_percent = psutil.virtual_memory().percent
    
    logger.info(f"Home requested - Bot: {bot_status}, Watchdog: {watchdog_status}")
    
    return jsonify({
        "status": "success",
        "message": "سرویس AZEN Entertainment در حال اجراست",
        "service": "AZEN Entertainment Telegram Bot",
        "version": "1.0.0",
        "system_info": {
            "bot_status": bot_status,
            "watchdog_status": watchdog_status,
            "cpu_usage": f"{cpu_percent}%",
            "memory_usage": f"{memory_percent}%",
            "uptime": f"{get_uptime()} seconds"
        }
    })

@app.route('/health')
def health():
    bot_status = get_bot_status()
    watchdog_status = get_watchdog_status()
    
    if bot_status == "running":
        status = "healthy"
    elif watchdog_status == "running":
        status = "recovering"
    else:
        status = "unhealthy"

    logger.info(f"Health check - Bot: {bot_status}, Watchdog: {watchdog_status}")

    return jsonify({
        "status": status,
        "components": {
            "telegram_bot": bot_status,
            "watchdog": watchdog_status
        },
        "timestamp": time.time()
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
