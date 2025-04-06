import logging
import traceback
import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from telegram.error import (TelegramError, Unauthorized, BadRequest,
                            TimedOut, NetworkError)
from config import (
    FAQ_TEXT, BROADCAST_PLATFORMS_TEXT, DISCOUNT_CODES_TEXT, 
    REFERRAL_PROGRAM_TEXT, MULTILINGUAL_CATALOG_TEXT, TALENT_SEARCH_CRITERIA,
    VOICE_ACTORS, ADMIN_CHAT_ID
)
from helpers import (
    build_main_menu_keyboard, build_genre_keyboard, build_talent_keyboard,
    build_support_keyboard, build_features_keyboard, build_vote_actor_keyboard,
    build_direct_message_keyboard, get_tracking_status, get_actor_info, 
    analyze_voice_sample, log_user_action
)
from logger_config import (
    main_logger as logger,
    log_user_interaction,
    log_error,
    log_message_forwarding,
    log_admin_action
)

# تابع نمایش منوی اصلی
def show_main_menu(update: Update, context: CallbackContext):
    """Show the main menu."""
    text = (
        "🎬 به ربات AZEN Entertainment خوش آمدی دوست عزیزم 🎬\n\n"
        "از طریق این ربات می‌توانید:\n"
        "🎤 نمونه صدای خود را برای همکاری ارسال کنید\n"
        "🔎 آثار دوبله شده ما را مشاهده کنید\n"
        "🎯 در تست‌های استعدادیابی شرکت کنید\n"
        "📞 با پشتیبانی ما در ارتباط باشید\n\n"
        "لطفاً از منوی زیر گزینه مورد نظر خود را انتخاب کنید:"
    )
    reply_markup = build_main_menu_keyboard()
    
    if update.callback_query:
        update.callback_query.edit_message_text(text=text, reply_markup=reply_markup)
    else:
        update.message.reply_text(text, reply_markup=reply_markup)
    
    log_user_action(update, "main_menu_view")

# دستور /start
def start(update: Update, context: CallbackContext):
    """Handle the /start command."""
    user = update.effective_user
    
    # اگر در یک گروه باشیم، ID گروه را نشان می‌دهیم
    if update.effective_chat.type in ['group', 'supergroup']:
        group_id = update.effective_chat.id
        update.message.reply_text(f"📝 اطلاعات گروه:\nنام: {update.effective_chat.title}\nشناسه: {group_id}\n\nلطفاً این شناسه را در فایل config.py در متغیر ADMIN_CHAT_ID قرار دهید.")
        logger.info(f"Bot added to group {update.effective_chat.title} with ID {group_id}")
        return
    
    welcome_text = (
        f"👋 سلام {user.first_name}!\n\n"
        f"🎬 به ربات AZEN Entertainment خوش آمدی دوست عزیزم 🎬\n\n"
        f"از طریق این ربات می‌توانید:\n"
        f"🎤 برای همکاری با تیم دوبلاژ ما نمونه صدای خود را ارسال کنید\n"
        f"📞 انتقادات، پیشنهادات و پیام‌های خودتون رو برای ما ارسال کنید\n\n"
        f"لطفاً از منوی زیر گزینه مورد نظر خود را انتخاب کنید."
    )
    update.message.reply_text(welcome_text, reply_markup=build_main_menu_keyboard())
    log_user_action(update, "start_command")

# دستور /help
def help_command(update: Update, context: CallbackContext):
    """Handle the /help command."""
    help_text = """📌 راهنمای استفاده از ربات AZEN Entertainment:

🔄 /start - شروع مجدد و نمایش منوی اصلی
ℹ️ /help - نمایش این راهنما 
❌ /cancel - لغو عملیات فعلی
🔗 /mylink - دریافت لینک معرفی دوستان

🎭 از طریق این ربات شما می‌توانید:
🎤 برای همکاری با تیم دوبلاژ ما نمونه صدای خود را ارسال کنید
📞 انتقادات، پیشنهادات و پیام‌های خودتون رو برای ما ارسال کنید

برای استفاده از امکانات ربات، از منوی اصلی گزینه مورد نظر خود را انتخاب کنید."""
    update.message.reply_text(help_text)
    log_user_action(update, "help_command")

# دستور /contact
def contact_command(update: Update, context: CallbackContext):
    """Handle the /contact command."""
    contact_text = """بخش ارتباط با ما:

لطفا پیام خود را ارسال کنید."""
    update.message.reply_text(contact_text)
    context.user_data['mode'] = 'contact_message'
    log_user_action(update, "contact_command")

# دستور /mylink
def mylink_command(update: Update, context: CallbackContext):
    """Handle the /mylink command to generate referral links."""
    user = update.effective_user
    referral_link = f"https://t.me/DubbingServiceBot?start=ref{user.id}"
    referral_text = f"""لینک معرفی دوستان شما:

{referral_link}

با اشتراک‌گذاری این لینک، برای هر دوست جدید ۱۰ امتیاز دریافت می‌کنید!"""
    update.message.reply_text(referral_text)
    log_user_action(update, "mylink_command")

# دستور /cancel
def cancel_command(update: Update, context: CallbackContext):
    """Handle the /cancel command to reset user state."""
    if 'mode' in context.user_data:
        del context.user_data['mode']
        update.message.reply_text("عملیات لغو شد. به منوی اصلی بازگشتید.")
    else:
        update.message.reply_text("عملیات فعالی برای لغو وجود ندارد.")
    
    show_main_menu(update, context)
    log_user_action(update, "cancel_command")

# هندلر دکمه‌های منو (Callback)
def button_handler(update: Update, context: CallbackContext):
    """Handle callback queries from inline keyboards."""
    query = update.callback_query
    query.answer()  # حذف حالت لودینگ در تلگرام
    data = query.data
    
    log_user_action(update, f"button_click_{data}")

    # بازگشت به منوی اصلی
    if data == 'main_menu':
        show_main_menu(update, context)
        
    # نمایش سوالات متداول
    elif data == 'faq':
        keyboard = [[InlineKeyboardButton("🏠 بازگشت به منوی اصلی", callback_data='main_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text=FAQ_TEXT, reply_markup=reply_markup)
        
    # نمایش اطلاعات تماس
    elif data == 'contact_support' or data == 'contact_us':
        text = """📞 ارتباط با ما:

لطفاً پیام خود را برای تیم AZEN Entertainment ارسال کنید.
تمامی پیام‌های شما به مدیریت ارسال خواهد شد."""
        keyboard = [[InlineKeyboardButton("🏠 بازگشت به منوی اصلی", callback_data='main_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text=text, reply_markup=reply_markup)
        context.user_data['mode'] = 'contact_message'

    elif data.startswith('genre_'):
        genre = data.split('_')[1]
        genre_names = {
            'comedy': 'کمدی',
            'action': 'اکشن',
            'drama': 'درام',
            'animation': 'انیمیشن',
            'documentary': 'مستند',
            'horror': 'ترسناک'
        }
        genre_name = genre_names.get(genre, genre)
        
        text = f"شما ژانر {genre_name} را انتخاب کرده‌اید.\n"
        text += f"نمونه‌های دوبله شده در ژانر {genre_name}:\n\n"
        
        # Adding sample dubbed works for each genre
        if genre == 'comedy':
            text += "1. فیلم کمدی «خانواده خوشبخت» - ۲۰۲۲\n"
            text += "2. سریال «در حاشیه ۲» - فصل اول\n"
            text += "3. انیمیشن «مینیون‌ها» - دوبله جدید\n"
        elif genre == 'action':
            text += "1. فیلم «ماموریت غیرممکن ۷» - ۲۰۲۳\n"
            text += "2. سریال «واکینگ دد» - فصل ۱۱\n"
            text += "3. فیلم «سریع و خشمگین ۱۰» - ۲۰۲۳\n"
        elif genre == 'drama':
            text += "1. فیلم «پدرخوانده» - نسخه جدید\n"
            text += "2. سریال «تاج» - فصل ۵\n"
            text += "3. فیلم «زندگی زیباست» - دوبله جدید\n"
        elif genre == 'animation':
            text += "1. انیمیشن «روح» - محصول پیکسار\n"
            text += "2. انیمیشن «لوکا» - دوبله اختصاصی\n"
            text += "3. سریال انیمیشنی «سیمپسون‌ها» - فصل ۳۲\n"
        elif genre == 'documentary':
            text += "1. مستند «سیاره زمین» - بی‌بی‌سی\n"
            text += "2. مستند «زندگی در اقیانوس‌ها» - نشنال جئوگرافیک\n"
            text += "3. مستند «انسان» - محصول ۲۰۲۲\n"
        elif genre == 'horror':
            text += "1. فیلم «احضار ۳» - ۲۰۲۱\n"
            text += "2. سریال «آمریکایی‌های ترسناک» - فصل ۱۰\n"
            text += "3. فیلم «آن - قسمت ۲» - دوبله جدید\n"
        
        text += "\nبرای دریافت نمونه صوتی یا فایل کامل، لطفاً نام اثر را ارسال کنید یا با پشتیبانی تماس بگیرید."
        
        keyboard = [
            [InlineKeyboardButton("بازگشت به لیست ژانرها", callback_data='dubbed_works')],
            [InlineKeyboardButton("بازگشت به منو", callback_data='main_menu')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text=text, reply_markup=reply_markup)
    
    # بخش استعدادیابی
    elif data == 'talent':
        text = "بخش استعدادیابی:\nلطفاً یکی از گزینه‌های زیر را انتخاب کنید:"
        reply_markup = build_talent_keyboard()
        query.edit_message_text(text=text, reply_markup=reply_markup)

    elif data == 'submit_talent':
        context.user_data['mode'] = 'talent_search'
        text = "لطفاً نمونه صدای خود را ارسال کنید تا سیستم تحلیل اولیه انجام شود.\n\n"
        text += "راهنمای ارسال نمونه صدا:\n"
        text += "- فایل صوتی باید واضح و بدون نویز پس‌زمینه باشد\n"
        text += "- مدت زمان: حداقل ۳۰ ثانیه و حداکثر ۲ دقیقه\n"
        text += "- یک متن ادبی یا دیالوگ فیلم را با احساس مناسب بخوانید\n"
        text += "- از تنوع لحن و صدا استفاده کنید"
        query.edit_message_text(text=text)

    elif data == 'voice_test':
        context.user_data['mode'] = 'voice_test'
        test_text = """لطفاً متن زیر را با صدای خود دوبله کنید و فایل صوتی را ارسال نمایید:

«زندگی مثل یک جعبه شکلات می‌مونه. هیچوقت نمی‌دونی چی گیرت میاد.»

در ضبط خود سعی کنید احساس مناسب را منتقل کنید."""
        query.edit_message_text(test_text)

    elif data == 'talent_criteria':
        query.edit_message_text(
            text=TALENT_SEARCH_CRITERIA,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("بازگشت", callback_data='talent')]])
        )

    # بخش همکاری با ما
    elif data == 'collaboration':
        context.user_data['mode'] = 'collaboration_voice_test'
        text = """🎭 همکاری با AZEN Entertainment 🎭

با سلام به شما علاقه‌مند به همکاری با تیم AZEN 👋

ما در AZEN به دنبال استعدادهای برتر در زمینه صداپیشگی و گویندگی هستیم. اگر فکر می‌کنید صدای خاص و جذابی دارید، این فرصت را از دست ندهید!

💼 شرایط همکاری:
🎤 میکروفون با کیفیت مناسب
🎞️ آشنایی با نرم‌افزارهای ویرایش ویدیو
🎭 آشنایی با مهارت صدا بازیگری
🔊 محیط ضبط با حداقل نویز محیطی

برای شروع همکاری، لطفاً یک نمونه صدا از خود ارسال کنید."""
        
        keyboard = [[InlineKeyboardButton("▶️ ارسال نمونه صدا", callback_data='collaboration_next')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text=text, reply_markup=reply_markup)
        
    elif data == 'collaboration_next':
        context.user_data['mode'] = 'collaboration_voice_test'
        text = """🎤 متن تست صدا 🎤

لطفاً متن زیر را بخوانید و در قالب یک ویس ارسال کنید:

💡 نکته: اگر توانایی تیپ گویی و صحبت با چند صدای مختلف را دارید حتما در خوانش متن از آن استفاده کنید و قبل از ارسال ویس متن را تمرین کنید.

😠 **شخصیت اول** (خشمگین، همراه با طعنه):  
"این همه سال گذشت... فکر کردی می‌شه فراموش کرد؟ یادت رفته چیکار کردی؟!"  

😔 **شخصیت دوم** (لرزان، با صدایی شکسته):  
"می‌دونم... می‌دونم. ولی اگه یه بار دیگه فرصت می‌دادی... شاید جبران می‌کردم..."  

😤 **شخصیت اول** (با طعنه و خشم):  
"جبران؟! مثل اینه که آیینه رو بشکنی و توقع داشته باشی تصویر سالمی نشون بده!"  

😌 **شخصیت سوم** (آرام، منطقی):  
"هردوتون بس کنید. این جنگِ گذشته، آینده رو نابود می‌کنه. باید راهی برای زمان حال‌مون پیدا کنیم."  

😰 **شخصیت دوم** (مضطرب):  
"راه... راه کجاست؟ همه‌چیز سیاهه... حتی نمیتونم جلوی پامو ببینم!"  

🙂 **شخصیت سوم** (امیدوار):  
"اگه تاریکی نباشه که دیگه نور معنایی نداره. شاید کافیه یکم بگردیم.."  

😏 **شخصیت اول** (تلخ، با خنده‌ای خشک):  
"خیلی خوش خیالی! ما اینجا گیر افتادیم. مسیرمون گم شده میفهمی؟"

💪 **شخصیت سوم** (مصمم، با لحنی محکم):  
"تنها چیزی که گم شده، *شهامت* ماست. بلند شید... همین الان شروع می‌کنیم."

🎬 لطفاً این متن را با صداهای متفاوت برای هر شخصیت ضبط کنید و ارسال نمایید."""
        keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data='collaboration')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text=text, reply_markup=reply_markup)
    
    # بخش پیگیری سفارش
    elif data == 'order_tracking':
        context.user_data['mode'] = 'order_tracking'
        text = "لطفاً کد پیگیری سفارش خود را ارسال کنید.\n(کد پیگیری ۶ رقمی است)"
        query.edit_message_text(text=text)
    
    # بخش پشتیبانی
    elif data == 'support':
        text = "بخش پشتیبانی:\nلطفاً یکی از گزینه‌های زیر را انتخاب کنید:"
        reply_markup = build_support_keyboard()
        query.edit_message_text(text=text, reply_markup=reply_markup)

    elif data == 'faq':
        keyboard = [[InlineKeyboardButton("بازگشت به پشتیبانی", callback_data='support')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text=FAQ_TEXT, reply_markup=reply_markup)
    
    elif data == 'report_issue':
        context.user_data['mode'] = 'report_issue'
        text = """لطفاً مشکل فنی خود را به صورت متنی ارسال کنید تا تیم پشتیبانی بررسی کند.

برای گزارش دقیق‌تر، موارد زیر را ذکر کنید:
1. نوع مشکل (مالی، فنی، کیفیت دوبله و...)
2. تاریخ بروز مشکل
3. جزئیات مشکل
4. در صورت وجود، شماره سفارش مرتبط

تیم پشتیبانی در اسرع وقت پاسخگوی شما خواهد بود."""
        query.edit_message_text(text=text)
    
    elif data == 'voice_comment':
        context.user_data['mode'] = 'voice_comment'
        text = "لطفاً کامنت صوتی خود را ارسال کنید. تیم ما به زودی پاسخ خواهد داد."
        query.edit_message_text(text=text)
    
    elif data == 'contact_support':
        text = """راه‌های ارتباط با ما:

📞 تلفن: ۰۲۱-۱۲۳۴۵۶۷۸

ساعات پاسخگویی: شنبه تا پنجشنبه، ۹ صبح تا ۵ عصر"""
        keyboard = [[InlineKeyboardButton("بازگشت به منو", callback_data='main_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text=text, reply_markup=reply_markup)
    
    # بخش امکانات ویژه
    elif data == 'features':
        text = "بخش امکانات ویژه:\nلطفاً یکی از گزینه‌های زیر را انتخاب کنید:"
        reply_markup = build_features_keyboard()
        query.edit_message_text(text=text, reply_markup=reply_markup)

    # امکانات ویژه - کاتالوگ چندزبانه
    elif data == 'multilingual_catalog':
        keyboard = [[InlineKeyboardButton("بازگشت به امکانات ویژه", callback_data='features')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text=MULTILINGUAL_CATALOG_TEXT, reply_markup=reply_markup)
    
    # امکانات ویژه - رأی‌گیری گوینده
    elif data == 'vote_actor':
        text = "لطفاً گوینده مورد نظر خود را انتخاب کنید:"
        reply_markup = build_vote_actor_keyboard()
        query.edit_message_text(text=text, reply_markup=reply_markup)
    
    # ثبت رأی گوینده
    elif data.startswith('vote_actor_'):
        actor_id = data.split('_')[-1]
        actor = VOICE_ACTORS.get(actor_id)
        if actor:
            # در یک برنامه واقعی، اینجا رأی در پایگاه داده ذخیره می‌شود
            VOICE_ACTORS[actor_id]['votes'] += 1
            text = f"رأی شما برای گوینده {actor['name']} ثبت شد. با تشکر از مشارکت شما."
        else:
            text = "گوینده انتخاب شده نامعتبر است. لطفاً مجدداً تلاش کنید."
        
        keyboard = [[InlineKeyboardButton("بازگشت به لیست گویندگان", callback_data='vote_actor')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text=text, reply_markup=reply_markup)
    
    elif data == 'actor_info':
        text = "اطلاعات گویندگان:\n\n"
        for actor_id, actor in VOICE_ACTORS.items():
            text += f"👤 {actor['name']}\n"
            text += f"تخصص: {actor['specialty']}\n"
            text += f"تعداد آرا: {actor['votes']}\n\n"
        
        keyboard = [[InlineKeyboardButton("بازگشت به رأی‌گیری", callback_data='vote_actor')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text=text, reply_markup=reply_markup)
    
    # امکانات ویژه - پلتفرم‌های پخش
    elif data == 'broadcast_platforms':
        keyboard = [[InlineKeyboardButton("بازگشت به امکانات ویژه", callback_data='features')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text=BROADCAST_PLATFORMS_TEXT, reply_markup=reply_markup)
    
    # امکانات ویژه - اطلاع‌رسانی آثار جدید
    elif data == 'announcement':
        text = """🎬 آثار جدید اضافه شده به مجموعه دوبله:

1. سریال «چرنوبیل» - فصل کامل (۵ قسمت)
2. فیلم «تنت» (۲۰۲۰) - دوبله اختصاصی با ۵ گوینده
3. انیمیشن «لوکا» (۲۰۲۱) - دوبله فارسی
4. مستند «دیوید آتنبرو: زندگی ما در سیاره ما» (۲۰۲۰)
5. فیلم «کروئلا» (۲۰۲۱) - دوبله اختصاصی

برای دسترسی به این آثار، به سایت ما مراجعه کنید یا با پشتیبانی تماس بگیرید.

🔔 برای دریافت اطلاعیه‌های جدید، به کانال ما بپیوندید: @DubbingChannel"""
        keyboard = [[InlineKeyboardButton("بازگشت به امکانات ویژه", callback_data='features')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text=text, reply_markup=reply_markup)
    
    # امکانات ویژه - کدهای تخفیف
    elif data == 'discount_codes':
        keyboard = [[InlineKeyboardButton("بازگشت به امکانات ویژه", callback_data='features')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text=DISCOUNT_CODES_TEXT, reply_markup=reply_markup)
    
    # امکانات ویژه - برنامه معرفی دوستان
    elif data == 'referral_program':
        keyboard = [[InlineKeyboardButton("بازگشت به امکانات ویژه", callback_data='features')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text=REFERRAL_PROGRAM_TEXT, reply_markup=reply_markup)
    
    else:
        query.edit_message_text("گزینه انتخاب شده نامعتبر است. لطفاً مجدداً تلاش کنید.")

# هندلر پیام‌های متنی و صوتی
def message_handler(update: Update, context: CallbackContext):
    """Handle text and voice messages."""
    mode = context.user_data.get('mode', None)

    if update.message.voice:
        # دریافت پیام صوتی
        log_user_action(update, f"received_voice_{mode}")
        
        if mode in ['talent_search', 'voice_test']:
            # تحلیل صوتی
            response = analyze_voice_sample(update, mode)
            update.message.reply_text(response)
            context.user_data['mode'] = None  # ریست کردن حالت پس از تحلیل
            
            # نمایش دکمه بازگشت به منو
            keyboard = [[InlineKeyboardButton("بازگشت به منو", callback_data='main_menu')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text("برای بازگشت به منوی اصلی کلیک کنید:", reply_markup=reply_markup)
        
        elif mode == 'collaboration_voice_test':
            # تحلیل نمونه همکاری و ارسال به مدیر
            user = update.effective_user
            username = user.username if user.username else "بدون یوزرنیم"
            
            # ثبت اطلاعات در لاگ
            log_user_action(
                update, 
                "collaboration_voice_submission",
                f"User ID: {user.id}, Username: @{username}"
            )
            
            # ارسال پیام به مدیر
            try:
                # آماده‌سازی پیام
                admin_msg = (
                    f"🎙️ نمونه صدای جدید برای همکاری:\n"
                    f"👤 {user.first_name} {user.last_name if user.last_name else ''}\n"
                    f"🆔 @{username}\n"
                    f"شناسه: {user.id}\n"
                    f"تاریخ ارسال: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )
                
                # بررسی صحت شناسه گروه مدیریت
                if not isinstance(ADMIN_CHAT_ID, int):
                    raise ValueError(f"Invalid ADMIN_CHAT_ID format: {ADMIN_CHAT_ID}")
                
                # ایجاد دکمه ارسال پیام مستقیم به کاربر
                reply_markup = build_direct_message_keyboard(user.id)
                
                # ارسال پیام متنی به گروه مدیریت همراه با دکمه ارسال پیام مستقیم
                message_sent = context.bot.send_message(
                    chat_id=ADMIN_CHAT_ID, 
                    text=admin_msg,
                    reply_markup=reply_markup
                )
                
                if message_sent:
                    # ثبت موفقیت ارسال پیام
                    log_message_forwarding(user.id, ADMIN_CHAT_ID, True)
                    log_admin_action(ADMIN_CHAT_ID, "received_application_info", f"From user {user.id}")
                
                # فوروارد کردن فایل صوتی به مدیر
                voice_sent = context.bot.forward_message(
                    chat_id=ADMIN_CHAT_ID,
                    from_chat_id=update.effective_chat.id,
                    message_id=update.message.message_id
                )
                
                if voice_sent:
                    # ثبت موفقیت ارسال فایل صوتی
                    logger.info(f"Voice sample from {user.id} forwarded to admin group {ADMIN_CHAT_ID}")
                    log_message_forwarding(user.id, ADMIN_CHAT_ID, True, "Voice message forwarded successfully")
                
            except ValueError as ve:
                # خطای مربوط به شناسه نامعتبر گروه
                error_msg = str(ve)
                logger.error(f"Admin group ID error: {error_msg}")
                log_error("ADMIN_ID_ERROR", error_msg, user_id=user.id)
                log_message_forwarding(user.id, ADMIN_CHAT_ID, False, f"Invalid admin group ID: {error_msg}")
                
            except BadRequest as br:
                # خطای درخواست نامعتبر تلگرام
                error_msg = str(br)
                logger.error(f"Telegram API BadRequest: {error_msg}")
                log_error("TELEGRAM_API_ERROR", error_msg, user_id=user.id)
                log_message_forwarding(user.id, ADMIN_CHAT_ID, False, f"Bad request: {error_msg}")
                
            except Unauthorized as ue:
                # ربات از گروه مدیریت حذف شده است
                error_msg = str(ue)
                logger.error(f"Bot removed from admin group: {error_msg}")
                log_error("ADMIN_GROUP_ACCESS", error_msg, user_id=user.id)
                log_message_forwarding(user.id, ADMIN_CHAT_ID, False, "Bot not authorized in admin group")
                
            except Exception as e:
                # سایر خطاها
                error_msg = str(e)
                logger.error(f"Error forwarding message to admin: {error_msg}")
                log_error("MESSAGE_FORWARDING", error_msg, user_id=user.id)
                log_message_forwarding(user.id, ADMIN_CHAT_ID, False, f"General error: {error_msg}")
            
            # پاسخ به کاربر
            update.message.reply_text(
                "✅ نمونه صدای شما با موفقیت دریافت شد و توسط مدیریت بررسی خواهد شد!\n\n"
                "تیم استعدادیابی AZEN Entertainment پس از بررسی صدای شما، در صورت تایید با شما تماس خواهد گرفت.\n\n"
                "🙏 با تشکر از مشارکت شما."
            )
            context.user_data['mode'] = None  # ریست کردن حالت
            
            # نمایش دکمه بازگشت به منو
            keyboard = [[InlineKeyboardButton("🏠 بازگشت به منوی اصلی", callback_data='main_menu')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text("برای بازگشت به منوی اصلی کلیک کنید:", reply_markup=reply_markup)
            
        elif mode == 'voice_comment':
            user = update.effective_user
            username = user.username if user.username else "بدون یوزرنیم"
            
            # ثبت اطلاعات در لاگ
            log_user_action(
                update, 
                "voice_comment_submission",
                f"User ID: {user.id}, Username: @{username}"
            )
            
            # ارسال پیام به مدیر
            try:
                # آماده‌سازی پیام
                admin_msg = (
                    f"🎤 کامنت صوتی جدید از:\n"
                    f"👤 {user.first_name} {user.last_name if user.last_name else ''}\n"
                    f"🆔 @{username}\n"
                    f"شناسه: {user.id}\n"
                    f"تاریخ ارسال: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )
                
                # بررسی صحت شناسه گروه مدیریت
                if not isinstance(ADMIN_CHAT_ID, int):
                    raise ValueError(f"Invalid ADMIN_CHAT_ID format: {ADMIN_CHAT_ID}")
                
                # ایجاد دکمه ارسال پیام مستقیم به کاربر
                reply_markup = build_direct_message_keyboard(user.id)
                
                # ارسال پیام متنی به گروه مدیریت همراه با دکمه ارسال پیام مستقیم
                message_sent = context.bot.send_message(
                    chat_id=ADMIN_CHAT_ID, 
                    text=admin_msg,
                    reply_markup=reply_markup
                )
                
                if message_sent:
                    # ثبت موفقیت ارسال پیام
                    log_message_forwarding(user.id, ADMIN_CHAT_ID, True)
                
                # فوروارد کردن فایل صوتی به مدیر
                voice_sent = context.bot.forward_message(
                    chat_id=ADMIN_CHAT_ID,
                    from_chat_id=update.effective_chat.id,
                    message_id=update.message.message_id
                )
                
                if voice_sent:
                    # ثبت موفقیت ارسال فایل صوتی
                    logger.info(f"Voice comment from {user.id} forwarded to admin group {ADMIN_CHAT_ID}")
                    log_message_forwarding(user.id, ADMIN_CHAT_ID, True, "Voice comment forwarded successfully")
                
            except ValueError as ve:
                # خطای مربوط به شناسه نامعتبر گروه
                error_msg = str(ve)
                logger.error(f"Admin group ID error: {error_msg}")
                log_error("ADMIN_ID_ERROR", error_msg, user_id=user.id)
                log_message_forwarding(user.id, ADMIN_CHAT_ID, False, f"Invalid admin group ID: {error_msg}")
                
            except BadRequest as br:
                # خطای درخواست نامعتبر تلگرام
                error_msg = str(br)
                logger.error(f"Telegram API BadRequest: {error_msg}")
                log_error("TELEGRAM_API_ERROR", error_msg, user_id=user.id)
                log_message_forwarding(user.id, ADMIN_CHAT_ID, False, f"Bad request: {error_msg}")
                
            except Unauthorized as ue:
                # ربات از گروه مدیریت حذف شده است
                error_msg = str(ue)
                logger.error(f"Bot removed from admin group: {error_msg}")
                log_error("ADMIN_GROUP_ACCESS", error_msg, user_id=user.id)
                log_message_forwarding(user.id, ADMIN_CHAT_ID, False, "Bot not authorized in admin group")
                
            except Exception as e:
                # سایر خطاها
                error_msg = str(e)
                logger.error(f"Error forwarding voice comment to admin: {error_msg}")
                log_error("MESSAGE_FORWARDING", error_msg, user_id=user.id)
                log_message_forwarding(user.id, ADMIN_CHAT_ID, False, f"General error: {error_msg}")
            
            update.message.reply_text("✅ کامنت صوتی شما با موفقیت دریافت شد و توسط مدیریت پاسخ داده خواهد شد. 🙏")
            context.user_data['mode'] = None
            
            # نمایش دکمه بازگشت به منو
            keyboard = [[InlineKeyboardButton("🏠 بازگشت به منوی اصلی", callback_data='main_menu')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text("برای بازگشت به منوی اصلی کلیک کنید:", reply_markup=reply_markup)
            
        elif mode == 'contact_message' and update.message.voice:
            user = update.effective_user
            username = user.username if user.username else "بدون یوزرنیم"
            
            # ثبت اطلاعات در لاگ
            log_user_action(
                update, 
                "contact_voice_message_submission",
                f"User ID: {user.id}, Username: @{username}"
            )
            
            # ارسال پیام به مدیر
            try:
                # آماده‌سازی پیام
                admin_msg = (
                    f"🎤 پیام صوتی جدید از:\n"
                    f"👤 {user.first_name} {user.last_name if user.last_name else ''}\n"
                    f"🆔 @{username}\n"
                    f"شناسه: {user.id}\n"
                    f"تاریخ ارسال: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )
                
                # بررسی صحت شناسه گروه مدیریت
                if not isinstance(ADMIN_CHAT_ID, int):
                    raise ValueError(f"Invalid ADMIN_CHAT_ID format: {ADMIN_CHAT_ID}")
                
                # ایجاد دکمه ارسال پیام مستقیم به کاربر
                reply_markup = build_direct_message_keyboard(user.id)
                
                # ارسال پیام متنی به گروه مدیریت همراه با دکمه ارسال پیام مستقیم
                message_sent = context.bot.send_message(
                    chat_id=ADMIN_CHAT_ID, 
                    text=admin_msg,
                    reply_markup=reply_markup
                )
                
                if message_sent:
                    # ثبت موفقیت ارسال پیام
                    log_message_forwarding(user.id, ADMIN_CHAT_ID, True)
                    log_admin_action(ADMIN_CHAT_ID, "received_voice_info", f"From user {user.id}")
                
                # فوروارد کردن فایل صوتی به مدیر
                voice_sent = context.bot.forward_message(
                    chat_id=ADMIN_CHAT_ID,
                    from_chat_id=update.effective_chat.id,
                    message_id=update.message.message_id
                )
                
                if voice_sent:
                    # ثبت موفقیت ارسال فایل صوتی
                    logger.info(f"Voice message from {user.id} forwarded to admin group {ADMIN_CHAT_ID}")
                    log_message_forwarding(user.id, ADMIN_CHAT_ID, True, "Voice message forwarded successfully")
                
            except ValueError as ve:
                # خطای مربوط به شناسه نامعتبر گروه
                error_msg = str(ve)
                logger.error(f"Admin group ID error: {error_msg}")
                log_error("ADMIN_ID_ERROR", error_msg, user_id=user.id)
                log_message_forwarding(user.id, ADMIN_CHAT_ID, False, f"Invalid admin group ID: {error_msg}")
                
            except BadRequest as br:
                # خطای درخواست نامعتبر تلگرام
                error_msg = str(br)
                logger.error(f"Telegram API BadRequest: {error_msg}")
                log_error("TELEGRAM_API_ERROR", error_msg, user_id=user.id)
                log_message_forwarding(user.id, ADMIN_CHAT_ID, False, f"Bad request: {error_msg}")
                
            except Unauthorized as ue:
                # ربات از گروه مدیریت حذف شده است
                error_msg = str(ue)
                logger.error(f"Bot removed from admin group: {error_msg}")
                log_error("ADMIN_GROUP_ACCESS", error_msg, user_id=user.id)
                log_message_forwarding(user.id, ADMIN_CHAT_ID, False, "Bot not authorized in admin group")
                
            except Exception as e:
                # سایر خطاها
                error_msg = str(e)
                logger.error(f"Error forwarding voice message to admin: {error_msg}")
                log_error("MESSAGE_FORWARDING", error_msg, user_id=user.id)
                log_message_forwarding(user.id, ADMIN_CHAT_ID, False, f"General error: {error_msg}")
            
            update.message.reply_text("✅ پیام صوتی شما با موفقیت دریافت شد و توسط مدیریت پاسخ داده خواهد شد. 🙏")
            context.user_data['mode'] = None
            
            # نمایش دکمه بازگشت به منو
            keyboard = [[InlineKeyboardButton("🏠 بازگشت به منوی اصلی", callback_data='main_menu')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text("برای بازگشت به منوی اصلی کلیک کنید:", reply_markup=reply_markup)
            
        else:
            update.message.reply_text("پیام صوتی دریافت شد.")
            # بجای نمایش منوی اصلی، فقط دکمه بازگشت نمایش داده شود
            keyboard = [[InlineKeyboardButton("🏠 بازگشت به منوی اصلی", callback_data='main_menu')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text("برای بازگشت به منوی اصلی کلیک کنید:", reply_markup=reply_markup)
            
    elif update.message.text:
        user_text = update.message.text.strip()
        log_user_action(update, f"received_text_{mode}")
        
        # در حالت پیگیری سفارش
        if mode == 'order_tracking' and user_text.isdigit():
            status = get_tracking_status(user_text)
            update.message.reply_text(f"وضعیت سفارش با کد {user_text}: {status}")
            context.user_data['mode'] = None
            
            # نمایش دکمه بازگشت به منو
            keyboard = [[InlineKeyboardButton("بازگشت به منو", callback_data='main_menu')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text("برای بازگشت به منوی اصلی کلیک کنید:", reply_markup=reply_markup)
            
        # در حالت همکاری
        elif mode == 'collaboration':
            update.message.reply_text(
                "اطلاعات همکاری شما با موفقیت دریافت شد و توسط مدیریت بررسی خواهد شد. "
                "با تشکر از علاقه شما به همکاری با AZEN Entertainment."
            )
            context.user_data['mode'] = None
            
            # نمایش دکمه بازگشت به منو
            keyboard = [[InlineKeyboardButton("بازگشت به منو", callback_data='main_menu')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text("برای بازگشت به منوی اصلی کلیک کنید:", reply_markup=reply_markup)
            
        # در حالت گزارش مشکل
        elif mode == 'report_issue':
            ticket_id = f"TIC-{hash(user_text) % 10000:04d}"
            update.message.reply_text(
                f"گزارش مشکل شما با شماره پیگیری {ticket_id} با موفقیت ثبت شد و توسط مدیریت بررسی خواهد شد. "
                "تیم پشتیبانی AZEN Entertainment در اسرع وقت به شما پاسخ خواهد داد."
            )
            context.user_data['mode'] = None
            
            # نمایش دکمه بازگشت به منو
            keyboard = [[InlineKeyboardButton("بازگشت به منو", callback_data='main_menu')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text("برای بازگشت به منوی اصلی کلیک کنید:", reply_markup=reply_markup)
            
        # در حالت تماس با ما
        elif mode == 'contact_message':
            user = update.effective_user
            username = user.username if user.username else "بدون یوزرنیم"
            
            # ثبت اطلاعات در لاگ
            log_user_action(
                update, 
                "contact_message_submission",
                f"User ID: {user.id}, Username: @{username}, Message: {user_text[:50]}..."
            )
            
            # ارسال پیام به مدیر
            try:
                # آماده‌سازی پیام
                admin_msg = (
                    f"💬 پیام جدید از:\n"
                    f"👤 {user.first_name} {user.last_name if user.last_name else ''}\n"
                    f"🆔 @{username}\n"
                    f"شناسه: {user.id}\n"
                    f"تاریخ ارسال: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                    f"✉️ متن پیام:\n{user_text}"
                )
                
                # بررسی صحت شناسه گروه مدیریت
                if not isinstance(ADMIN_CHAT_ID, int):
                    raise ValueError(f"Invalid ADMIN_CHAT_ID format: {ADMIN_CHAT_ID}")
                
                # ایجاد دکمه ارسال پیام مستقیم به کاربر
                reply_markup = build_direct_message_keyboard(user.id)
                
                # ارسال پیام متنی به گروه مدیریت همراه با دکمه ارسال پیام مستقیم
                message_sent = context.bot.send_message(
                    chat_id=ADMIN_CHAT_ID, 
                    text=admin_msg,
                    reply_markup=reply_markup
                )
                
                if message_sent:
                    # ثبت موفقیت ارسال پیام
                    logger.info(f"Text message from {user.id} forwarded to admin group {ADMIN_CHAT_ID}")
                    log_message_forwarding(user.id, ADMIN_CHAT_ID, True, "Text message forwarded successfully")
                    log_admin_action(ADMIN_CHAT_ID, "received_text_message", f"From user {user.id}")
                
            except ValueError as ve:
                # خطای مربوط به شناسه نامعتبر گروه
                error_msg = str(ve)
                logger.error(f"Admin group ID error: {error_msg}")
                log_error("ADMIN_ID_ERROR", error_msg, user_id=user.id)
                log_message_forwarding(user.id, ADMIN_CHAT_ID, False, f"Invalid admin group ID: {error_msg}")
                
            except BadRequest as br:
                # خطای درخواست نامعتبر تلگرام
                error_msg = str(br)
                logger.error(f"Telegram API BadRequest: {error_msg}")
                log_error("TELEGRAM_API_ERROR", error_msg, user_id=user.id)
                log_message_forwarding(user.id, ADMIN_CHAT_ID, False, f"Bad request: {error_msg}")
                
            except Unauthorized as ue:
                # ربات از گروه مدیریت حذف شده است
                error_msg = str(ue)
                logger.error(f"Bot removed from admin group: {error_msg}")
                log_error("ADMIN_GROUP_ACCESS", error_msg, user_id=user.id)
                log_message_forwarding(user.id, ADMIN_CHAT_ID, False, "Bot not authorized in admin group")
                
            except Exception as e:
                # سایر خطاها
                error_msg = str(e)
                logger.error(f"Error forwarding text message to admin: {error_msg}")
                log_error("MESSAGE_FORWARDING", error_msg, user_id=user.id)
                log_message_forwarding(user.id, ADMIN_CHAT_ID, False, f"General error: {error_msg}")
            
            update.message.reply_text(
                "✅ پیام شما با موفقیت دریافت شد و توسط مدیریت پاسخ داده خواهد شد. 🙏"
            )
            context.user_data['mode'] = None
            
            # نمایش دکمه بازگشت به منو
            keyboard = [[InlineKeyboardButton("🏠 بازگشت به منوی اصلی", callback_data='main_menu')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text("برای بازگشت به منوی اصلی کلیک کنید:", reply_markup=reply_markup)
            
        else:
            # اگر در حالت خاصی نیست، فقط دکمه بازگشت به منو را نمایش می‌دهیم
            keyboard = [[InlineKeyboardButton("🏠 بازگشت به منوی اصلی", callback_data='main_menu')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text("برای بازگشت به منوی اصلی کلیک کنید:", reply_markup=reply_markup)

# هندلر برای خطاها
def error_handler(update: Update, context: CallbackContext):
    """Log errors and send a message to the user."""
    # گرفتن اطلاعات خطا
    error_msg = str(context.error)
    try:
        # اطلاعات خطا را با جزئیات ثبت می‌کنیم
        trace = "".join(traceback.format_tb(context.error.__traceback__))
        
        # دسته‌بندی خطا برای مدیریت بهتر
        error_type = "GENERAL_ERROR"
        user_id = None
        
        if update and update.effective_user:
            user_id = update.effective_user.id
            username = update.effective_user.username or "no_username"
            log_user_interaction(user_id, username, "error_encountered", f"Error: {error_msg}")
        
        # تشخیص نوع خطا
        if isinstance(context.error, Unauthorized):
            error_type = "UNAUTHORIZED"
            log_error(error_type, f"Bot was blocked by user: {error_msg}", user_id=user_id)
            # از این خطا می‌گذریم چون کاربر ربات را بلاک کرده است
            return
            
        elif isinstance(context.error, BadRequest):
            error_type = "BAD_REQUEST"
            log_error(error_type, f"Bad request: {error_msg}", user_id=user_id)
            
        elif isinstance(context.error, TimedOut):
            error_type = "TIMED_OUT"
            log_error(error_type, f"Request timed out: {error_msg}", user_id=user_id)
            # معمولا نیازی به پاسخ به کاربر نیست
            return
            
        elif isinstance(context.error, NetworkError):
            error_type = "NETWORK_ERROR"
            log_error(error_type, f"Network error: {error_msg}", user_id=user_id)
            
        else:
            # ثبت جزئیات کامل خطا
            log_error(
                error_type, 
                f"Unexpected error: {error_msg}", 
                user_id=user_id, 
                additional_info=f"Traceback: {trace}"
            )
            
        # ثبت کامل خطا در لاگ اصلی
        logger.error(f"Update {update} caused error {context.error}\nTraceback: {trace}")
        
        # ارسال پیام به کاربر (اگر ممکن باشد)
        if update and update.effective_message:
            try:
                # پیام خطای مناسب بر اساس نوع خطا
                error_text = "متأسفانه خطایی رخ داده است. لطفاً مجدداً تلاش کنید یا با پشتیبانی تماس بگیرید."
                
                if isinstance(context.error, BadRequest):
                    error_text = "درخواست نامعتبر است. لطفاً از دستور /start برای شروع مجدد استفاده کنید."
                elif isinstance(context.error, NetworkError):
                    error_text = "خطای شبکه رخ داده است. لطفاً اتصال اینترنت خود را بررسی کرده و مجدداً تلاش کنید."
                
                update.effective_message.reply_text(error_text)
                
            except Exception as send_error:
                log_error("ERROR_HANDLER", f"Failed to send error message: {send_error}", user_id=user_id)
                
    except Exception as e:
        # خطا در خود error handler
        logger.error(f"Critical: Error in error handler: {e}")
        log_error("ERROR_HANDLER_FAILURE", str(e))
