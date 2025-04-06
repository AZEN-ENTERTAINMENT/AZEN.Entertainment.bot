from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from config import TRACKING_STATUS, VOICE_ACTORS
from logger_config import (
    main_logger as logger,
    log_user_interaction,
    log_error,
    log_message_forwarding
)

def build_direct_message_keyboard(user_id):
    """ایجاد دکمه برای ارسال پیام مستقیم به کاربر.
    
    Args:
        user_id: شناسه کاربر برای ارسال پیام مستقیم
        
    Returns:
        InlineKeyboardMarkup: کیبورد با دکمه ارسال پیام مستقیم
    """
    keyboard = [
        [InlineKeyboardButton("✉️ ارسال پیام مستقیم به کاربر", url=f"tg://user?id={user_id}")]
    ]
    return InlineKeyboardMarkup(keyboard)

def build_main_menu_keyboard():
    """Create the main menu keyboard."""
    keyboard = [
        [InlineKeyboardButton("🎭 همکاری با ما 🎭", callback_data='collaboration')],
        [InlineKeyboardButton("📞 ارتباط با ما", callback_data='contact_us')]
    ]
    return InlineKeyboardMarkup(keyboard)

def build_genre_keyboard():
    """Create a keyboard for selecting genres."""
    keyboard = [
        [InlineKeyboardButton("کمدی", callback_data='genre_comedy'),
         InlineKeyboardButton("اکشن", callback_data='genre_action')],
        [InlineKeyboardButton("درام", callback_data='genre_drama'),
         InlineKeyboardButton("انیمیشن", callback_data='genre_animation')],
        [InlineKeyboardButton("مستند", callback_data='genre_documentary'),
         InlineKeyboardButton("ترسناک", callback_data='genre_horror')],
        [InlineKeyboardButton("بازگشت به منو", callback_data='main_menu')]
    ]
    return InlineKeyboardMarkup(keyboard)

def build_talent_keyboard():
    """Create a keyboard for talent search options."""
    keyboard = [
        [InlineKeyboardButton("ارسال نمونه برای استعدادیابی", callback_data='submit_talent')],
        [InlineKeyboardButton("آزمون صدا", callback_data='voice_test')],
        [InlineKeyboardButton("معیارهای استعدادیابی", callback_data='talent_criteria')],
        [InlineKeyboardButton("بازگشت به منو", callback_data='main_menu')]
    ]
    return InlineKeyboardMarkup(keyboard)

def build_support_keyboard():
    """Create a keyboard for support options."""
    keyboard = [
        [InlineKeyboardButton("سوالات متداول", callback_data='faq'),
         InlineKeyboardButton("گزارش مشکل", callback_data='report_issue')],
        [InlineKeyboardButton("ارسال کامنت صوتی", callback_data='voice_comment')],
        [InlineKeyboardButton("تماس با ما", callback_data='contact_support')],
        [InlineKeyboardButton("بازگشت به منو", callback_data='main_menu')]
    ]
    return InlineKeyboardMarkup(keyboard)

def build_features_keyboard():
    """Create a keyboard for special features."""
    keyboard = [
        [InlineKeyboardButton("کاتالوگ چندزبانه", callback_data='multilingual_catalog')],
        [InlineKeyboardButton("رأی‌گیری گوینده", callback_data='vote_actor')],
        [InlineKeyboardButton("پلتفرم‌های پخش", callback_data='broadcast_platforms')],
        [InlineKeyboardButton("اطلاع رسانی آثار جدید", callback_data='announcement')],
        [InlineKeyboardButton("کدهای تخفیف", callback_data='discount_codes')],
        [InlineKeyboardButton("برنامه معرفی دوستان", callback_data='referral_program')],
        [InlineKeyboardButton("بازگشت به منو", callback_data='main_menu')]
    ]
    return InlineKeyboardMarkup(keyboard)

def build_vote_actor_keyboard():
    """Create a keyboard for voice actor voting."""
    keyboard = [
        [InlineKeyboardButton(f"گوینده الف ({VOICE_ACTORS['A']['name']})", callback_data='vote_actor_A'),
         InlineKeyboardButton(f"گوینده ب ({VOICE_ACTORS['B']['name']})", callback_data='vote_actor_B')],
        [InlineKeyboardButton(f"گوینده ج ({VOICE_ACTORS['C']['name']})", callback_data='vote_actor_C')],
        [InlineKeyboardButton("اطلاعات بیشتر", callback_data='actor_info')],
        [InlineKeyboardButton("بازگشت به منو", callback_data='main_menu')]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_tracking_status(tracking_code):
    """Get the status of an order by tracking code."""
    return TRACKING_STATUS.get(tracking_code, "کد پیگیری نامعتبر است. لطفاً کد صحیح را وارد کنید.")

def get_actor_info(actor_id):
    """Get information about a voice actor."""
    actor = VOICE_ACTORS.get(actor_id)
    if actor:
        return f"اطلاعات گوینده {actor['name']}:\n" \
               f"تخصص: {actor['specialty']}\n" \
               f"تعداد آرا: {actor['votes']}"
    return "اطلاعات گوینده یافت نشد."

def analyze_voice_sample(update: Update, mode):
    """Analyze a voice sample for talent search or voice test."""
    # In a real application, you would use voice processing libraries
    # For now, we'll return a simulated response
    if mode == 'talent_search':
        return ("نمونه صوتی شما دریافت و تحلیل شد.\n"
                "صدای شما پتانسیل مناسبی برای دوبله دارد. "
                "تیم ما در اسرع وقت با شما تماس خواهد گرفت.\n\n"
                "نتایج تحلیل اولیه:\n"
                "- تنوع تن صدا: خوب\n"
                "- شفافیت بیان: عالی\n"
                "- کنترل احساسات: متوسط\n"
                "- تناسب با شخصیت‌ها: خوب")
    elif mode == 'voice_test':
        return ("آزمون صدا انجام شد. نتایج اولیه:\n"
                "- تطابق با متن: 85%\n"
                "- کیفیت صدا: خوب\n"
                "- وضوح کلمات: عالی\n\n"
                "صدای شما برای پروژه‌های ما مناسب است.")
    return "پیام صوتی دریافت شد. با تشکر."

def log_user_action(update: Update, action, additional_info=None):
    """Log user actions for analytics."""
    user = update.effective_user
    username = user.username if user.username else "no_username"
    
    # ثبت در لاگ قدیمی برای سازگاری
    logger.info(f"User {user.id} (@{username}) performed action: {action}")
    
    # ثبت در سیستم لاگینگ جدید با جزئیات بیشتر
    try:
        log_user_interaction(
            user_id=user.id,
            username=username,
            action=action,
            details=additional_info
        )
    except Exception as e:
        # ثبت خطای ناشی از لاگینگ
        log_error("LOGGING", str(e), user_id=user.id, additional_info=f"Failed to log action: {action}")
