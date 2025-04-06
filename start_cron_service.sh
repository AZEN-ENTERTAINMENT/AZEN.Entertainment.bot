#!/bin/bash

# اسکریپت راه‌اندازی سرویس زمان‌بندی شده
echo "Starting Scheduled Restart Service..."
python cron_restart.py >> logs/cron_service_output.log 2>&1 &
echo "Scheduled Restart Service started in background."
