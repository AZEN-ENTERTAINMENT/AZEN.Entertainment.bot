#!/bin/bash

# اسکریپت راه‌اندازی سرویس پینگ
echo "Starting Server Ping service..."
python server_ping.py >> logs/ping_service_output.log 2>&1 &
echo "Server Ping service started in background."