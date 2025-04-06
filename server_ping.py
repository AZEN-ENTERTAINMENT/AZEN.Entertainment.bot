#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اسکریپت نگه دارنده سرور (Server Ping)
این اسکریپت به صورت دوره‌ای به آدرس‌های مختلف درخواست می‌زند تا سرور همیشه فعال بماند
"""

import time
import logging
import threading
import requests
import os

# تنظیمات لاگینگ
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    filename='logs/ping_service.log',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger("ping_service")

# آدرس‌های سرور که باید پینگ شوند
SERVER_URLS = [
    # آدرس داخلی سرور ربات تلگرام
    "http://localhost:8080/health",
    # آدرس سرور اتصال خارجی
    "http://localhost:3000/ping",
    # URL عمومی پروژه شما روی Replit (هنگام Deploy)
    "https://AZEN-Telegram-Bot.replit.app/health"
]

# سعی در خواندن توکن
try:
    with open('token.txt', 'r') as token_file:
        TOKEN = token_file.read().strip()
except Exception:
    # اگر توکن وجود نداشت، یک توکن پیش‌فرض استفاده کنید
    TOKEN = "your-secret-key-here"

# آدرس سرور اتصال با توکن
if TOKEN != "your-secret-key-here":
    SERVER_URLS.append(f"http://localhost:3000/ping?token={TOKEN}")

# زمان بین هر پینگ (به ثانیه)
PING_INTERVAL = 5 * 60  # هر 5 دقیقه

def ping_server(url):
    """ارسال درخواست به سرور و ثبت نتیجه"""
    try:
        response = requests.get(url, timeout=10)
        logger.info(f"Pinged {url}: {response.status_code}")
        return True
    except Exception as e:
        logger.error(f"Failed to ping {url}: {str(e)}")
        return False

def ping_all_servers():
    """پینگ همه سرورها"""
    success_count = 0
    for url in SERVER_URLS:
        if ping_server(url):
            success_count += 1
    
    logger.info(f"Ping cycle completed: {success_count}/{len(SERVER_URLS)} servers reached")
    return success_count

def ping_loop():
    """حلقه اصلی پینگ کردن به صورت دوره‌ای"""
    while True:
        try:
            ping_all_servers()
        except Exception as e:
            logger.error(f"Error in ping loop: {str(e)}")
        
        # انتظار برای زمان بعدی
        time.sleep(PING_INTERVAL)

def start_ping_service():
    """راه‌اندازی سرویس پینگ در پس‌زمینه"""
    ping_thread = threading.Thread(target=ping_loop, daemon=True)
    ping_thread.start()
    logger.info("Ping service started")
    print("Ping service started in background.")
    return ping_thread

if __name__ == "__main__":
    print("Starting ping service...")
    thread = start_ping_service()
    print(f"Ping service running. Pinging {len(SERVER_URLS)} servers every {PING_INTERVAL} seconds.")
    print("Press Ctrl+C to stop.")
    
    # نگه داشتن برنامه اصلی در حال اجرا
    try:
        while thread.is_alive():
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping ping service...")
        print("Ping service will stop at next iteration.")