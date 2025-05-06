#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Persian Telegram Bot for Dubbing Service

This bot provides a user-friendly interface for a dubbing service, including:
- Browsing dubbed works by genre
- Talent scouting and voice testing
- Collaboration opportunities
- Order tracking
- Customer support
- Special features like discount codes and referral programs
"""

import logging
import time
import sys
import traceback
from telegram.ext import (
    Updater, CommandHandler, CallbackQueryHandler, 
    MessageHandler, Filters
)
from config import TOKEN, logger
from handlers import (
    start, help_command, contact_command, mylink_command, cancel_command,
    button_handler, message_handler, error_handler
)
from keep_alive import keep_alive

def main():
    """Run the bot."""
    # keep_alive()  # غیرفعال برای GitHub Actions، چون ورک‌فلو خودش ربات رو فعال نگه می‌داره
    
    try:
        # Create the Updater and pass it your bot's token
        updater = Updater(TOKEN)
        
        # Get the dispatcher to register handlers
        dp = updater.dispatcher
        
        # Set bot commands to display in the chat interface
        commands = [
            ('start', 'شروع کار با ربات'),
            ('help', 'راهنمای استفاده از ربات'),
            ('mylink', 'دریافت لینک معرفی دوستان'),
            ('cancel', 'لغو عملیات فعلی')
        ]
        
        # Set bot commands (this will display the commands in the message input field)
        updater.bot.set_my_commands(commands)
        
        # Add command handlers
        dp.add_handler(CommandHandler("start", start))
        dp.add_handler(CommandHandler("help", help_command))
        dp.add_handler(CommandHandler("contact", contact_command))
        dp.add_handler(CommandHandler("mylink", mylink_command))
        dp.add_handler(CommandHandler("cancel", cancel_command))
        
        # Add handler for inline keyboard buttons
        dp.add_handler(CallbackQueryHandler(button_handler))
        
        # Add handler for messages (text and voice)
        dp.add_handler(MessageHandler(Filters.text | Filters.voice, message_handler))
        
        # Add error handler
        dp.add_error_handler(error_handler)
        
        # Start the Bot
        logger.info("Starting bot...")
        while True:
            try:
                updater.start_polling()
                updater.idle()
            except Exception as e:
                logger.error(f"Polling error: {str(e)}")
                time.sleep(5)  # 5 ثانیه صبر قبل از تلاش دوباره
        
    except Exception as e:
        # ثبت خطا و تلاش برای راه‌اندازی مجدد
        error_trace = traceback.format_exc()
        logger.error(f"Bot crashed with error: {str(e)}\n{error_trace}")
        
        # اندکی مکث قبل از تلاش مجدد
        time.sleep(5)
        logger.info("Attempting to restart the bot...")
        main()  # راه‌اندازی مجدد ربات

if __name__ == '__main__':
    main()
