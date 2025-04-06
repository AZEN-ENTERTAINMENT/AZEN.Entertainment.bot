#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اسکریپت زمان‌بندی شده برای راه‌اندازی مجدد ربات
این اسکریپت به صورت دوره‌ای ربات را بررسی می‌کند و در صورت نیاز مجدداً راه‌اندازی می‌کند.
"""

import os
import time
import logging
import subprocess
import psutil
import threading
import schedule
from datetime import datetime

# تنظیمات لاگینگ
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    filename='logs/cron_restart.log',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger("cron_restart")

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

def restart_bot():
    """بررسی وضعیت ربات و راه‌اندازی مجدد آن در صورت نیاز"""
    logger.info("Running scheduled check for bot status...")
    
    if not is_bot_running():
        logger.warning("Bot is not running! Attempting to restart...")
        try:
            # تلاش برای اجرای اسکریپت اصلی راه‌اندازی
            subprocess.run(['bash', 'startup.sh'], 
                          stdout=subprocess.PIPE, 
                          stderr=subprocess.PIPE,
                          check=True)
            logger.info("Startup script executed successfully")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to execute startup script: {str(e)}")
            
            # تلاش مستقیم برای راه‌اندازی ربات
            try:
                subprocess.Popen(['python', 'bot.py'],
                                stdout=open('logs/bot_restart.log', 'a'),
                                stderr=open('logs/bot_restart_error.log', 'a'),
                                start_new_session=True)
                logger.info("Direct bot restart attempted")
            except Exception as e2:
                logger.error(f"Failed to restart bot directly: {str(e2)}")
    else:
        logger.info("Bot is running properly")

def run_scheduler():
    """اجرای زمان‌بندی برای بررسی‌های دوره‌ای"""
    # زمان‌بندی برای بررسی هر 30 دقیقه
    schedule.every(30).minutes.do(restart_bot)
    
    # زمان‌بندی برای بررسی در ساعات خاص
    schedule.every().day.at("00:00").do(restart_bot)  # نیمه شب
    schedule.every().day.at("06:00").do(restart_bot)  # صبح
    schedule.every().day.at("12:00").do(restart_bot)  # ظهر
    schedule.every().day.at("18:00").do(restart_bot)  # عصر
    
    logger.info("Scheduler initialized with regular checks")
    
    # بررسی اولیه هنگام راه‌اندازی
    restart_bot()
    
    # حلقه اصلی اجرای زمان‌بندی
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)  # بررسی هر دقیقه
        except Exception as e:
            logger.error(f"Error in scheduler loop: {str(e)}")
            time.sleep(300)  # در صورت خطا، 5 دقیقه صبر می‌کنیم

if __name__ == "__main__":
    logger.info("Starting scheduled restart checker...")
    
    # اجرای زمان‌بندی در یک ترد جداگانه
    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.daemon = True
    scheduler_thread.start()
    
    logger.info("Scheduled restart checker is running in background")
    print("Scheduled restart checker started. Check logs/cron_restart.log for details.")
    
    # نگه داشتن برنامه اصلی در حال اجرا
    try:
        while scheduler_thread.is_alive():
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping scheduled restart checker...")
        print("Service will stop at next iteration.")