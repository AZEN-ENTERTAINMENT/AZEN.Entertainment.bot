#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اسکریپت حفظ زنده بودن ربات تلگرام
این اسکریپت یک سرور وب ساده ایجاد می‌کند که همیشه فعال نگه داشته می‌شود
و از طریق یک سرویس مانیتورینگ خارجی (مانند UptimeRobot) قابل دسترسی است.
"""

import threading
import logging
import time
from flask import Flask, jsonify

# تنظیمات لاگینگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logger = logging.getLogger("keep_alive")

# ایجاد برنامه فلسک
app = Flask(__name__)

@app.route('/')
def home():
    """صفحه اصلی برای بررسی وضعیت ربات."""
    return jsonify({
        'status': 'online',
        'message': 'AZEN Entertainment Telegram Bot is running',
        'timestamp': time.time()
    })

@app.route('/health')
def health():
    """مسیر بررسی سلامت برای سرویس‌های مانیتورینگ."""
    return jsonify({
        'status': 'healthy',
        'telegram_bot': 'running',
        'timestamp': time.time()
    })

def run():
    """راه‌اندازی سرور در یک ترد جداگانه."""
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    """راه‌اندازی سرور فلسک در پس‌زمینه."""
    server_thread = threading.Thread(target=run)
    server_thread.daemon = True  # اجرای برنامه به عنوان یک ترد دیمون
    server_thread.start()
    logger.info("Keep-alive server started on port 8080")