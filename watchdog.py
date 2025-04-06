#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اسکریپت مراقبت از ربات تلگرام
این اسکریپت به طور مداوم وضعیت ربات را بررسی می‌کند و در صورت مشاهده مشکل، آن را مجدداً راه‌اندازی می‌کند.
"""

import os
import time
import sys
import subprocess
import logging
import signal
import psutil
import requests
from datetime import datetime

# تنظیمات لاگینگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO,
    handlers=[
        logging.FileHandler("logs/watchdog.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("watchdog")

# متغیرهای پیکربندی
BOT_PROCESS_NAME = "bot.py"  # نام فایل اصلی ربات
HEALTH_CHECK_URL = "http://localhost:8080/health"  # آدرس بررسی سلامت
CHECK_INTERVAL = 60  # فاصله زمانی بررسی وضعیت (ثانیه)
MAX_RESTART_ATTEMPTS = 5  # حداکثر تعداد تلاش برای راه‌اندازی مجدد
RESTART_COOLDOWN = 300  # زمان انتظار بین تلاش‌های راه‌اندازی مجدد (ثانیه)

def is_bot_running():
    """بررسی اینکه آیا ربات در حال اجراست یا خیر."""
    try:
        # بررسی پروسه از طریق نام
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            if BOT_PROCESS_NAME in ' '.join(proc.info['cmdline'] or []):
                return True
    except:
        pass
    
    # بررسی از طریق API وضعیت سلامت
    try:
        response = requests.get(HEALTH_CHECK_URL, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'healthy' and data.get('telegram_bot') == 'running':
                return True
    except:
        pass
    
    return False

def start_bot():
    """راه‌اندازی ربات."""
    try:
        logger.info("Starting Telegram bot...")
        # اجرای ربات به صورت پس‌زمینه
        subprocess.Popen(["python", "bot.py"], 
                         stdout=open("logs/bot_stdout.log", "a"),
                         stderr=open("logs/bot_stderr.log", "a"))
        
        # اندکی صبر برای راه‌اندازی
        time.sleep(10)
        
        # بررسی موفقیت‌آمیز بودن راه‌اندازی
        if is_bot_running():
            logger.info("Bot successfully started!")
            return True
        else:
            logger.error("Failed to start the bot.")
            return False
    except Exception as e:
        logger.error(f"Error starting bot: {str(e)}")
        return False

def main():
    """تابع اصلی نظارت بر ربات."""
    logger.info("Watchdog service started.")
    restart_attempts = 0
    
    while True:
        try:
            # بررسی وضعیت ربات
            if not is_bot_running():
                logger.warning("Telegram bot is not running!")
                
                # تلاش برای راه‌اندازی مجدد
                if restart_attempts < MAX_RESTART_ATTEMPTS:
                    restart_attempts += 1
                    logger.info(f"Attempting to restart the bot (attempt {restart_attempts}/{MAX_RESTART_ATTEMPTS})...")
                    
                    if start_bot():
                        restart_attempts = 0  # ریست کردن شمارنده تلاش‌ها در صورت موفقیت
                    else:
                        logger.error(f"Restart attempt {restart_attempts} failed.")
                        
                        # در صورت رسیدن به حداکثر تلاش‌ها، برای مدت طولانی‌تری صبر می‌کنیم
                        if restart_attempts >= MAX_RESTART_ATTEMPTS:
                            logger.critical(f"Maximum restart attempts reached. Cooling down for {RESTART_COOLDOWN/60} minutes.")
                            time.sleep(RESTART_COOLDOWN)
                            restart_attempts = 0  # ریست کردن شمارنده برای تلاش‌های جدید
                else:
                    # این بخش نباید اجرا شود، اما برای اطمینان
                    logger.critical("Maximum restart attempts exceeded. Resetting counter.")
                    restart_attempts = 0
            else:
                # ربات فعال است
                logger.info("Telegram bot is running properly.")
                restart_attempts = 0  # ریست کردن شمارنده در صورت فعال بودن

            # مکث قبل از بررسی بعدی
            time.sleep(CHECK_INTERVAL)
            
        except Exception as e:
            logger.error(f"Error in watchdog process: {str(e)}")
            time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    # بررسی و ایجاد دایرکتوری لاگ
    os.makedirs("logs", exist_ok=True)
    
    # راه‌اندازی نظارت‌گر
    main()