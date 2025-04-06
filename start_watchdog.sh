#!/bin/bash

# اسکریپت راه‌اندازی watchdog برای مانیتورینگ ربات
echo "Starting Telegram bot watchdog service..."
python watchdog.py >> logs/watchdog_output.log 2>&1 &
echo "Watchdog service started in background."