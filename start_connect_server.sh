#!/bin/bash

# اسکریپت راه‌اندازی سرور اتصال خارجی
echo "Starting Connection Server..."
python connect.py > logs/connect_server.log 2>&1 &
echo "Connection Server started on port 3000."