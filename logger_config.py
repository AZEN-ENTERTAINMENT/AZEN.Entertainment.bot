#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging
import datetime
from logging.handlers import RotatingFileHandler

# مسیر برای ذخیره فایل‌های لاگ
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# تنظیمات لاگر اصلی
def setup_logger():
    # ایجاد لاگر اصلی
    logger = logging.getLogger("azen_bot")
    logger.setLevel(logging.DEBUG)
    
    # فرمت لاگ‌ها
    formatter = logging.Formatter(
        '%(asctime)s - [%(levelname)s] - %(name)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    
    # تنظیمات نمایش در کنسول
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # تنظیمات فایل لاگ کلی
    general_log_file = os.path.join(LOG_DIR, "bot.log")
    file_handler = RotatingFileHandler(
        general_log_file, maxBytes=5*1024*1024, backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    
    # تنظیمات فایل لاگ خطاها
    error_log_file = os.path.join(LOG_DIR, "errors.log")
    error_file_handler = RotatingFileHandler(
        error_log_file, maxBytes=5*1024*1024, backupCount=5
    )
    error_file_handler.setLevel(logging.ERROR)
    error_file_handler.setFormatter(formatter)
    
    # تنظیمات فایل لاگ تعاملات کاربران
    user_log_file = os.path.join(LOG_DIR, "user_interactions.log")
    user_file_handler = RotatingFileHandler(
        user_log_file, maxBytes=5*1024*1024, backupCount=5
    )
    user_file_handler.setLevel(logging.INFO)
    user_file_handler.setFormatter(formatter)
    
    # لاگر تعاملات کاربر
    user_logger = logging.getLogger("azen_bot.user_interactions")
    user_logger.addHandler(user_file_handler)
    
    # لاگر عملیات ادمین
    admin_log_file = os.path.join(LOG_DIR, "admin_operations.log")
    admin_file_handler = RotatingFileHandler(
        admin_log_file, maxBytes=5*1024*1024, backupCount=5
    )
    admin_file_handler.setLevel(logging.INFO)
    admin_file_handler.setFormatter(formatter)
    
    admin_logger = logging.getLogger("azen_bot.admin")
    admin_logger.addHandler(admin_file_handler)
    
    # افزودن تمام handler ها به لاگر اصلی
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.addHandler(error_file_handler)
    
    return logger

# لاگر اصلی
main_logger = setup_logger()

# لاگرهای تخصصی
user_logger = logging.getLogger("azen_bot.user_interactions")
admin_logger = logging.getLogger("azen_bot.admin")
error_logger = logging.getLogger("azen_bot.errors")

# توابع راحتی برای لاگینگ

def log_user_interaction(user_id, username, action, details=None):
    """ثبت تعامل کاربر در لاگ"""
    log_msg = f"USER:{user_id} - @{username} - ACTION:{action}"
    if details:
        log_msg += f" - DETAILS:{details}"
    user_logger.info(log_msg)

def log_admin_action(admin_id, action, details=None):
    """ثبت اقدامات مدیر در لاگ"""
    log_msg = f"ADMIN:{admin_id} - ACTION:{action}"
    if details:
        log_msg += f" - DETAILS:{details}"
    admin_logger.info(log_msg)

def log_message_forwarding(from_user_id, to_chat_id, success, error_message=None):
    """ثبت وضعیت ارسال پیام به گروه مدیریت"""
    if success:
        admin_logger.info(f"Message forwarded successfully: FROM_USER:{from_user_id} TO_CHAT:{to_chat_id}")
    else:
        error_msg = f"Message forwarding failed: FROM_USER:{from_user_id} TO_CHAT:{to_chat_id}"
        if error_message:
            error_msg += f" - ERROR:{error_message}"
        error_logger.error(error_msg)

def log_error(error_type, error_message, user_id=None, additional_info=None):
    """ثبت خطاها با جزئیات کامل"""
    error_msg = f"ERROR_TYPE:{error_type} - MESSAGE:{error_message}"
    if user_id:
        error_msg += f" - USER:{user_id}"
    if additional_info:
        error_msg += f" - ADDITIONAL_INFO:{additional_info}"
    error_logger.error(error_msg)