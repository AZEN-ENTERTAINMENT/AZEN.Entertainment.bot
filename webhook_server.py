# webhook_server.py
# Wrapper webhook برای AZEN.Entertainment.bot
#
# توضیح: این فایل طوری نوشته شده که اگر ربات شما از aiogram (نسخه 2.x) استفاده کند،
# بدون تغییر در فایل‌های اصلی، درخواستهای تلگرام را به dispatcher ارسال می‌کند.
# اگر از نسخه‌ی دیگری استفاده می‌کنید یا اسم اشیا در bot.py فرق دارد،
# کافیست 2 نام بالایی (from bot import ...) را مناسب تغییر دهید.

import os
import asyncio
from typing import Dict, Any

from fastapi import FastAPI, Request, Response
import uvicorn

# --- اینجا اسم ماژولی که ربات را تعریف کرده است وارد کن ---
# معمولاً در مخزن شما نام فایل bot.py است که dispatcher و bot را می‌سازد.
# اگر در bot.py اسم dispatcher یا bot متفاوت است، این import را مطابق آن تغییر بده.
try:
    # فرض پیش‌فرض: bot.py یک 'dp' (Dispatcher) و یک 'bot' (Bot) ساخته
    from bot import dp, bot
    from aiogram import types
    AIOTYPE = "aiogram_v2"
except Exception as e:
    # اگر import بالا نشد، سعی می‌کنیم با نام‌های دیگر مثل 'dispatcher' تست کنیم
    try:
        from bot import dispatcher as dp, bot
        from aiogram import types
        AIOTYPE = "aiogram_v2"
    except Exception as e2:
        raise RuntimeError("نشد bot و dp را از bot.py import کنم. لطفاً نام اشیاء dispatcher/bot را بررسی کن.") from e2

app = FastAPI()

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", None)
WEBHOOK_PATH = os.environ.get("WEBHOOK_PATH", "/webhook")
# URL عمومی که سرویس‌دهنده می‌دهد — بدون trailing slash
PUBLIC_URL = os.environ.get("PUBLIC_URL", None)  # مثال: https://yourapp.onrender.com

if not BOT_TOKEN:
    print("هشدار: متغیر محیطی TELEGRAM_BOT_TOKEN تنظیم نشده. هنگام deploy آن را قرار بده.")

@app.post(WEBHOOK_PATH)
async def telegram_webhook(request: Request):
    """
    دریافت payload از تلگرام و ارسال برای dispatcher.
    """
    try:
        data = await request.json()
    except Exception:
        return Response(content="bad request", status_code=400)

    # تبدیل به Update و پردازش توسط dispatcher (aiogram v2)
    try:
        update = types.Update.to_object(data)
    except Exception:
        # fallback: اگر to_object نبود، بسازیم دستی
        update = types.Update(**data)

    # برخی dispatcherها نیاز به فراخوانی async process_update دارند.
    loop = asyncio.get_event_loop()
    try:
        # در aiogram v2:
        loop.create_task(dp.process_update(update))
    except Exception as e:
        # گاهی dp.process_update نیاز به لیست دارد یا اسم متد فرق داره
        try:
            loop.create_task(dp.process_updates([update]))
        except Exception as e2:
            # آخرین تلاش: اگر dp.bot داشته باشد، از bot.process_new_updates استفاده کن
            try:
                loop.create_task(bot.process_new_updates([update]))
            except Exception as e3:
                print("خطا در فرستادن update به dispatcher:", e, e2, e3)
                return Response(content="dispatch error", status_code=500)

    return Response(content="ok", status_code=200)

# helper برای ست کردن webhook
async def set_webhook():
    """
    صدا زدن برای ست کردن webhook روی PUBLIC_URL + WEBHOOK_PATH
    """
    if not PUBLIC_URL:
        print("متغیر محیطی PUBLIC_URL مشخص نیست. قبل از اجرا آن را تنظیم کن.")
        return
    url = PUBLIC_URL.rstrip("/") + WEBHOOK_PATH
    print("در حال ست کردن webhook روی:", url)
    try:
        # aiogram Bot.set_webhook
        result = await bot.set_webhook(url)
        print("set_webhook result:", result)
    except Exception as e:
        print("خطا هنگام set_webhook:", e)

if __name__ == "__main__":
    # اگر خواستی لوکال تست کنی:
    # export TELEGRAM_BOT_TOKEN="..."; export PUBLIC_URL="https://..."; export WEBHOOK_PATH="/webhook"
    # سپس: python webhook_server.py
    # در حالت لوکال set_webhook اجرا می‌شود و uvicorn سرور را بالا می‌آورد.
    if PUBLIC_URL and BOT_TOKEN:
        asyncio.run(set_webhook())
    uvicorn.run("webhook_server:app", host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), log_level="info")
