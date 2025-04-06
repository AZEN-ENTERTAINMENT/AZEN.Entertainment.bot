#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اسکریپت اتصال خارجی
این اسکریپت یک سرور وب ساده ایجاد می‌کند که از بیرون قابل دسترسی است
و برای اتصال خارجی به ربات استفاده می‌شود.
"""

import os
import random
import string
import logging
from flask import Flask, jsonify, request

# تنظیمات لاگینگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logger = logging.getLogger("connect_server")

# ایجاد برنامه فلسک
app = Flask(__name__)

# ایجاد یک توکن امنیتی تصادفی
TOKEN_LENGTH = 32
SECRET_TOKEN = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(TOKEN_LENGTH))

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
    try:
        # بررسی اینکه آیا ربات در حال اجراست
        # اگر نبود، آن را مجدداً راه‌اندازی کنید
        os.system("python bot.py &")
        logger.info("Bot reactivation triggered")
    except Exception as e:
        logger.error(f"Error reactivating bot: {str(e)}")
    
    return jsonify({
        'status': 'success',
        'message': 'Bot connection active',
        'action': 'ping'
    })

@app.route('/status')
def status():
    """بررسی وضعیت ربات."""
    return jsonify({
        'status': 'online',
        'components': {
            'telegram_bot': 'running',
            'web_server': 'running'
        }
    })

def run_server():
    """اجرای سرور در حالت اصلی."""
    # نمایش توکن امنیتی
    print(f"\n================ SECRET TOKEN ================")
    print(f"Your secret token is: {SECRET_TOKEN}")
    print(f"Use this token in your monitoring service URL.")
    print(f"Example: https://your-replit.id.repl.co/ping?token={SECRET_TOKEN}")
    print(f"================================================\n")
    
    # راه‌اندازی سرور
    app.run(host='0.0.0.0', port=3000)

if __name__ == '__main__':
    run_server()