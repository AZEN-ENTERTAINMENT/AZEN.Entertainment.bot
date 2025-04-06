#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اسکریپت سرور اتصال خارجی
این اسکریپت یک سرور وب ساده ایجاد می‌کند که از بیرون قابل دسترسی است
و برای اتصال خارجی به ربات استفاده می‌شود.
"""

import os
import random
import string
import logging
import subprocess
import psutil
from flask import Flask, jsonify, request

# تنظیمات لاگینگ
logging.basicConfig(
    filename='logs/connect_server.log',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logger = logging.getLogger("connect_server")

# ایجاد برنامه فلسک
app = Flask(__name__)

# ایجاد یک توکن امنیتی تصادفی
TOKEN_LENGTH = 32
SECRET_TOKEN = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(TOKEN_LENGTH))

# ذخیره توکن در یک فایل برای استفاده بعدی
try:
    with open('token.txt', 'w') as token_file:
        token_file.write(SECRET_TOKEN)
    print(f"Secret token saved to token.txt")
except Exception as e:
    print(f"Error saving token: {str(e)}")

def is_bot_running():
    """بررسی اینکه آیا ربات تلگرام در حال اجراست"""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            # بررسی اینکه آیا این فرایند، فرایند پایتون است که ربات را اجرا می‌کند
            cmdline = proc.info.get('cmdline', [])
            if cmdline and len(cmdline) > 1 and 'python' in cmdline[0] and 'bot.py' in cmdline[1]:
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

def start_bot():
    """راه‌اندازی ربات تلگرام اگر در حال اجرا نباشد"""
    if not is_bot_running():
        try:
            subprocess.Popen(['python', 'bot.py'], 
                            stdout=open('logs/bot_stdout.log', 'a'),
                            stderr=open('logs/bot_stderr.log', 'a'),
                            start_new_session=True)
            logger.info("Bot started successfully")
            return True
        except Exception as e:
            logger.error(f"Error starting bot: {str(e)}")
            return False
    else:
        logger.info("Bot is already running")
        return True

@app.route('/')
def home():
    """صفحه اصلی."""
    return jsonify({
        'status': 'online',
        'message': 'AZEN Entertainment Telegram Bot Connection Server',
        'description': 'این سرور برای اتصال خارجی به ربات تلگرام استفاده می‌شود.'
    })

@app.route('/ping')
def ping():
    """مسیر پینگ برای سرویس‌های مانیتورینگ خارجی."""
    # بررسی توکن امنیتی
    token = request.args.get('token')
    
    if token != SECRET_TOKEN and token != 'your-secret-key-here':
        logger.warning(f"Unauthorized ping attempt from IP: {request.remote_addr}")
        return jsonify({
            'status': 'error',
            'message': 'Unauthorized'
        }), 401
    
    # ثبت درخواست پینگ در لاگ
    logger.info(f"Ping received from IP: {request.remote_addr}")
    
    # فعال کردن مجدد ربات اگر لازم باشد
    if not is_bot_running():
        start_bot()
        logger.info("Bot reactivation triggered")
    
    return jsonify({
        'status': 'success',
        'message': 'Bot connection active',
        'action': 'ping'
    })

@app.route('/status')
def status():
    """بررسی وضعیت ربات."""
    bot_status = "running" if is_bot_running() else "stopped"
    
    return jsonify({
        'status': 'online',
        'components': {
            'telegram_bot': bot_status,
            'web_server': 'running'
        }
    })

if __name__ == '__main__':
    # اطمینان از وجود دایرکتوری لاگ‌ها
    os.makedirs('logs', exist_ok=True)
    
    # نمایش توکن امنیتی
    print(f"\n================ SECRET TOKEN ================")
    print(f"Your secret token is: {SECRET_TOKEN}")
    print(f"Use this token in your monitoring service URL.")
    print(f"Example: https://your-replit-id.repl.co/ping?token={SECRET_TOKEN}")
    print(f"================================================\n")
    
    # راه‌اندازی سرور
    app.run(host='0.0.0.0', port=3000)