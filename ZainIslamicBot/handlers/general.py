from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import db
from language import get_text

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db.add_user(user.id, user.username, user.first_name, user.last_name)
    user_language = db.get_user_language(user.id)
    
    # FIXED: Use keyword argument
    welcome_text = get_text("welcome", user_language, name=user.first_name)
    
    if user_language == 'ar':
        commands_text = f"""
{get_text('commands', user_language)}

📖 {get_text('quran_services', user_language)}
/quran - تصفح جميع السور
/surah - قراءة سورة محددة

🕌 {get_text('prayer_times', user_language)}
/prayer - أوقات الصلاة لأي مدينة
/ramadan - معلومات رمضان

📚 {get_text('hadith_knowledge', user_language)}
/hadith - أحاديث عشوائية
/hadith_categories - أحاديث حسب التصنيف
/allah_names - أسماء الله الحسنى
/duas - أدعية يومية

🕋 {get_text('islamic_tools', user_language)}
/tools - أدوات إسلامية (قبلة، تقويم، زكاة)

*بارك الله فيك!* 🤲
        """
        
        keyboard = [
            [InlineKeyboardButton("📖 القرآن", callback_data="quran"),
             InlineKeyboardButton("🕌 أوقات الصلاة", callback_data="prayer")],
            [InlineKeyboardButton("📚 الحديث والمعرفة", callback_data="hadith_categories")],
            [InlineKeyboardButton("🕋 الأدوات الإسلامية", callback_data="tools_main")],
            [InlineKeyboardButton("🕋 أسماء الله الحسنى", callback_data="names_page_1")],
            [InlineKeyboardButton("🤲 الأدعية اليومية", callback_data="duas"),
             InlineKeyboardButton("🌙 English", callback_data="language_settings")]
        ]
    else:
        commands_text = f"""
{get_text('commands', user_language)}

📖 {get_text('quran_services', user_language)}
/quran - Browse all 114 Surahs
/surah - Read specific Surah

🕌 {get_text('prayer_times', user_language)}
/prayer - Prayer times for any city
/ramadan - Ramadan information

📚 {get_text('hadith_knowledge', user_language)}
/hadith - Random Hadith collection
/hadith_categories - Hadith by categories
/allah_names - 99 Names of Allah
/duas - Daily supplications

🕋 {get_text('islamic_tools', user_language)}
/tools - Islamic tools (Qibla, Calendar, Zakat)

*May Allah bless you!* 🤲
        """
        
        keyboard = [
            [InlineKeyboardButton("📖 Quran", callback_data="quran"),
             InlineKeyboardButton("🕌 Prayer Times", callback_data="prayer")],
            [InlineKeyboardButton("📚 Hadith & Knowledge", callback_data="hadith_categories")],
            [InlineKeyboardButton("🕋 Islamic Tools", callback_data="tools_main")],
            [InlineKeyboardButton("🕋 99 Names of Allah", callback_data="names_page_1")],
            [InlineKeyboardButton("🤲 Daily Duas", callback_data="duas"),
             InlineKeyboardButton("🌙 العربية", callback_data="language_settings")]
        ]
    
    full_welcome = welcome_text + commands_text
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(full_welcome, reply_markup=reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_language = db.get_user_language(update.effective_user.id)
    
    if user_language == 'ar':
        help_text = """
*🤖 بوت زين الإسلامي - المساعدة*

*خدمات القرآن:*
`/quran` - تصفح جميع السور
`/surah <رقم>` - قراءة سورة محددة

*أوقات الصلاة:*
`/prayer <مدينة>` - أوقات الصلاة للمدينة
`/ramadan` - معلومات رمضان

*الحديث والمعرفة:*
`/hadith` - أحاديث عشوائية
`/hadith_categories` - أحاديث حسب التصنيف
`/allah_names` - أسماء الله الحسنى
`/duas` - أدعية يومية

*الأدوات الإسلامية:*
`/tools` - أدوات إسلامية (قبلة، تقويم، زكاة)

*الدعم:*
للأسئلة أو المقترحات، اتصل بالمسؤول.
        """
    else:
        help_text = """
*🤖 Zain Islamic Bot - Help*

*Quran Commands:*
`/quran` - Browse all 114 Surahs
`/surah <number>` - Read specific Surah

*Prayer Commands:*
`/prayer <city>` - Prayer times for city
`/ramadan` - Ramadan information

*Islamic Knowledge:*
`/hadith` - Random Hadith
`/hadith_categories` - Hadith by categories
`/allah_names` - 99 Names of Allah
`/duas` - Daily supplications

*Islamic Tools:*
`/tools` - Islamic tools (Qibla, Calendar, Zakat)

*Support:*
For issues or suggestions, contact admin.
        """
    await update.message.reply_text(help_text)

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_language = db.get_user_language(update.effective_user.id)
    
    if user_language == 'ar':
        about_text = """
*🕌 حول بوت زين الإسلامي*

*الإصدار:* 2.0 (ثنائي اللغة)
*المطور:* زين
*اللغات:* العربية والإنجليزية
*الهدف:* تقديم المعرفة الإسلامية بلغات متعددة

*المميزات:*
• القرآن الكريم بالترجمة
• حساب أوقات الصلاة  
• مجموعة أحاديث محسنة
• أسماء الله الحسنى
• أدعية يومية
• واجهة ثنائية اللغة
• أدوات إسلامية (قبلة، تقويم، زكاة)

*تقبل الله جهودنا* 🤲
        """
    else:
        about_text = """
*🕌 About Zain Islamic Bot*

*Version:* 2.0 (Bilingual)
*Developer:* Zain
*Languages:* English & العربية
*Purpose:* To provide authentic Islamic knowledge in multiple languages

*Features:*
• Complete Quran with translations
• Prayer time calculations  
• Enhanced Hadith collection
• 99 Names of Allah
• Daily duas and supplications
• Bilingual interface
• Islamic tools (Qibla, Calendar, Zakat)

*May Allah accept our efforts!* 🤲
        """
    await update.message.reply_text(about_text)

async def language_settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_language = db.get_user_language(update.effective_user.id)
    
    if user_language == 'ar':
        text = """
🌙 *إعدادات اللغة*

اختر اللغة المفضلة:

*English* - للواجهة الإنجليزية
*العربية* - للواجهة العربية

سيتم تغيير جميع النصوص والقوائم إلى اللغة المختارة.
        """
        keyboard = [
            [InlineKeyboardButton("🇺🇸 English", callback_data="set_lang_en")],
            [InlineKeyboardButton("🇸🇦 العربية", callback_data="set_lang_ar")],
            [InlineKeyboardButton("↩️ العودة", callback_data="back_main")]
        ]
    else:
        text = """
🌙 *Language Settings*

Choose your preferred language:

*English* - For English interface
*العربية* - For Arabic interface

All texts and menus will change to the selected language.
        """
        keyboard = [
            [InlineKeyboardButton("🇺🇸 English", callback_data="set_lang_en")],
            [InlineKeyboardButton("🇸🇦 العربية", callback_data="set_lang_ar")],
            [InlineKeyboardButton("↩️ Back", callback_data="back_main")]
        ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(text, reply_markup=reply_markup)