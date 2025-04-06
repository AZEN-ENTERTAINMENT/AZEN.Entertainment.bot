from flask import Flask, render_template, jsonify
import psutil
import os
import time
import subprocess
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

def is_process_running(process_name):
    """بررسی آیا فرایند مشخصی در حال اجراست"""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        cmdline = ' '.join(proc.info['cmdline'] or [])
        if process_name in cmdline:
            return True
    return False

def get_bot_status():
    """دریافت وضعیت ربات تلگرام"""
    if is_process_running(BOT_PROCESS_NAME):
        return "running"
    else:
        return "stopped"

def get_watchdog_status():
    """دریافت وضعیت سیستم نظارت"""
    if is_process_running(WATCHDOG_PROCESS_NAME):
        return "running"
    else:
        return "stopped"

@app.route('/')
def home():
    """صفحه اصلی سرور"""
    # بررسی وضعیت ربات و سیستم نظارت
    bot_status = get_bot_status()
    watchdog_status = get_watchdog_status()
    
    # بررسی اطلاعات سیستم
    cpu_percent = psutil.cpu_percent()
    memory_percent = psutil.virtual_memory().percent
    
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
            "uptime": time.time()
        }
    })

@app.route('/health')
def health():
    """بررسی سلامت سیستم"""
    bot_status = get_bot_status()
    watchdog_status = get_watchdog_status()
    
    # تعیین وضعیت کلی سیستم
    if bot_status == "running":
        status = "healthy"
    else:
        if watchdog_status == "running":
            status = "recovering"  # واچداگ در حال فعالیت است و احتمالاً ربات را راه‌اندازی مجدد می‌کند
        else:
            status = "unhealthy"  # هم ربات و هم واچداگ متوقف شده‌اند
    
    return jsonify({
        "status": status,
        "components": {
            "telegram_bot": bot_status,
            "watchdog": watchdog_status
        },
        "timestamp": time.time()
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)