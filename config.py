import os
from logger_config import main_logger as logger, log_error

# Bot configuration
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    log_error("CONFIG", "No TELEGRAM_BOT_TOKEN found in environment variables")
    raise ValueError("No TELEGRAM_BOT_TOKEN found in environment variables!")

# Admin or manager group chat ID
ADMIN_CHAT_ID = -1002635622836  # ID گروه به صورت عدد

# تلاش برای ذخیره خطاهای احتمالی در شناسه گروه
try:
    if not isinstance(ADMIN_CHAT_ID, int):
        log_error("CONFIG", f"Invalid ADMIN_CHAT_ID format: {ADMIN_CHAT_ID}. Must be an integer.")
except Exception as e:
    log_error("CONFIG", f"Error validating ADMIN_CHAT_ID: {str(e)}")

# Sample texts for different sections
FAQ_TEXT = """❓ سوالات متداول ❓

س: چطور می‌توانم با گروه AZEN همکاری کنم؟
ج: از طریق همین ربات می‌توانید نمونه صدای خود را ارسال کنید. تیم ما پس از بررسی با شما تماس خواهد گرفت.

س: چه نوع صداهایی مورد نیاز است؟
ج: ما به دنبال صداهای متنوع و توانایی تقلید صدا (تیپ‌گویی) هستیم.

س: آیا داشتن تجربه قبلی ضروری است؟
ج: خیر، مهم‌ترین ویژگی استعداد و توانایی شماست. البته تجربه قبلی یک مزیت محسوب می‌شود.

س: چه امکاناتی برای همکاری نیاز است؟
ج: داشتن میکروفون با کیفیت مناسب و آشنایی با یک نرم‌افزار ویرایش ویدیویی ساده.

س: نحوه پرداخت به همکاران چگونه است؟
ج: پرداخت‌ها بر اساس پروژه و توافق طرفین صورت می‌گیرد. با افزایش تجربه، میزان پرداخت افزایش می‌یابد."""

BROADCAST_PLATFORMS_TEXT = """لیست پلتفرم‌های پخش:
- نتفلیکس: https://www.netflix.com
- آپارات: https://www.aparat.com
- فیلیمو: https://www.filimo.com
- نماوا: https://www.namava.ir
- تلوبیون: https://www.telewebion.com

برای دسترسی به آثار دوبله‌شده ما در هر پلتفرم، روی لینک کلیک کنید."""

DISCOUNT_CODES_TEXT = """کدهای تخفیف فعال:

1. کد تخفیف برای اولین سفارش: DUB20
   ۲۰٪ تخفیف برای مشتریان جدید

2. کد تخفیف ویژه پروژه‌های بلند: LONGDUB15
   ۱۵٪ تخفیف برای پروژه‌های بالای ۶۰ دقیقه

3. کد تخفیف مناسبتی: EID1402
   ۱۰٪ تخفیف به مناسبت عید

کدهای تخفیف را در هنگام ثبت سفارش وارد کنید.
تاریخ انقضا: ۱۴۰۲/۰۶/۳۱"""

REFERRAL_PROGRAM_TEXT = """برنامه معرفی دوستان:

1. با معرفی هر دوست، ۱۰ امتیاز دریافت کنید
2. هر ۵۰ امتیاز معادل ۱۵٪ تخفیف در سفارش بعدی شماست
3. دوستان شما نیز ۱۰٪ تخفیف در اولین سفارش دریافت می‌کنند

برای معرفی دوستان، لینک اختصاصی خود را از طریق دستور /mylink دریافت کنید.

اطلاعات بیشتر:
https://example.com/referral"""

MULTILINGUAL_CATALOG_TEXT = """کاتالوگ چندزبانه آثار:

1. فارسی - بیش از ۵۰۰ اثر دوبله شده به زبان فارسی
2. انگلیسی - ۳۰۰ اثر با دوبله انگلیسی
3. عربی - ۱۵۰ اثر با دوبله عربی
4. ترکی استانبولی - ۷۵ اثر با دوبله ترکی

برای دریافت کاتالوگ کامل، به وبسایت ما مراجعه کنید:
https://example.com/catalog

یا با شماره زیر تماس بگیرید:
021-12345678"""

TALENT_SEARCH_CRITERIA = """⭐ شرایط همکاری با گروه AZEN ⭐

🔍 نیازمندی‌های فنی:
🎤 میکروفون با کیفیت مناسب
🎞️ آشنایی با نرم‌افزارهای ویرایش صدا یا ویدیو
🔊 محیط ضبط با حداقل نویز محیطی

تجربه قبلی الزامی نیست، اما یک مزیت محسوب می‌شود."""

# Database mock (in a real application, you would use a proper database)
# This is just for demonstration purposes
TRACKING_STATUS = {
    "123456": "در حال پردازش - مرحله ضبط اولیه",
    "234567": "تکمیل شده - آماده تحویل",
    "345678": "در انتظار بررسی نهایی",
    "456789": "در صف انتظار",
    "567890": "تکمیل شده و تحویل داده شده",
}

# Voice actors data
VOICE_ACTORS = {
    "A": {"name": "علی محمدی", "specialty": "انیمیشن و مستند", "votes": 42},
    "B": {"name": "سارا احمدی", "specialty": "فیلم و سریال", "votes": 38},
    "C": {"name": "محمد رضایی", "specialty": "بازی‌های ویدیویی", "votes": 27},
}
