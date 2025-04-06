#!/bin/bash

# اسکریپت راه‌اندازی اصلی برای ربات تلگرام و سیستم‌های مرتبط
# این اسکریپت همه سرویس‌های لازم را راه‌اندازی می‌کند

# ایجاد دایرکتوری لاگ‌ها اگر وجود ندارد
mkdir -p logs

# ذخیره زمان شروع
echo "Start time: $(date)" > logs/startup_log.txt
echo "Starting AZEN Entertainment Telegram Bot system..." | tee -a logs/startup_log.txt

# راه‌اندازی ربات تلگرام
echo "Starting Telegram Bot..." | tee -a logs/startup_log.txt
python bot.py > logs/bot.log 2>&1 &
BOT_PID=$!
echo "Telegram Bot started with PID: $BOT_PID" | tee -a logs/startup_log.txt

# راه‌اندازی سیستم نظارت (watchdog)
echo "Starting Watchdog system..." | tee -a logs/startup_log.txt
bash start_watchdog.sh
echo "Watchdog system started" | tee -a logs/startup_log.txt

# راه‌اندازی سرویس پینگ
echo "Starting Server Ping service..." | tee -a logs/startup_log.txt
bash start_ping_service.sh
echo "Server Ping service started" | tee -a logs/startup_log.txt

# راه‌اندازی سرور اتصال خارجی
echo "Starting Connection Server..." | tee -a logs/startup_log.txt
bash start_connect_server.sh
echo "Connection Server started" | tee -a logs/startup_log.txt

# راه‌اندازی سرویس زمان‌بندی شده
echo "Starting Scheduled Restart Service..." | tee -a logs/startup_log.txt
bash start_cron_service.sh
echo "Scheduled Restart Service started" | tee -a logs/startup_log.txt

echo "All services started successfully!" | tee -a logs/startup_log.txt
echo "Bot is now running and being monitored." | tee -a logs/startup_log.txt
echo "Check logs directory for detailed logs." | tee -a logs/startup_log.txt
echo "System will stay active even when you're not connected." | tee -a logs/startup_log.txt
echo "=============================================" | tee -a logs/startup_log.txt
