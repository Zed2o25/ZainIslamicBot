from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import requests
from database import db

async def prayer_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_language = db.get_user_language(update.effective_user.id)
    
    # Get city from command arguments or use default
    if context.args:
        city = " ".join(context.args)
    else:
        city = "Mecca"  # Default city
    
    try:
        prayer_times = await get_prayer_times(city, user_language)
        
        if user_language == 'ar':
            keyboard = [
                [InlineKeyboardButton("🔄 تحديث", callback_data="prayer")],
                [InlineKeyboardButton("🏙️ مدينة أخرى", callback_data="enter_city_prayer")],
                [InlineKeyboardButton("↩️ العودة للرئيسية", callback_data="back_main")]
            ]
        else:
            keyboard = [
                [InlineKeyboardButton("🔄 Refresh", callback_data="prayer")],
                [InlineKeyboardButton("🏙️ Other City", callback_data="enter_city_prayer")],
                [InlineKeyboardButton("↩️ Back to Main", callback_data="back_main")]
            ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if hasattr(update, 'callback_query') and update.callback_query:
            await update.callback_query.edit_message_text(prayer_times, reply_markup=reply_markup)
        else:
            await update.message.reply_text(prayer_times, reply_markup=reply_markup)
        
    except Exception as e:
        print(f"Prayer error: {e}")
        if user_language == 'ar':
            await update.message.reply_text(f"❌ تعذر الحصول على أوقات الصلاة لـ {city}. يرجى المحاولة مرة أخرى.")
        else:
            await update.message.reply_text(f"❌ Could not fetch prayer times for {city}. Please try again.")

async def get_prayer_times(city: str, language: str):
    try:
        # Use a reliable prayer times API
        url = f"http://api.aladhan.com/v1/timingsByCity?city={city}&country=&method=2"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if data['code'] == 200:
            timings = data['data']['timings']
            date = data['data']['date']['readable']
            hijri = data['data']['date']['hijri']['date']
            hijri_day = data['data']['date']['hijri']['day']
            hijri_month_ar = data['data']['date']['hijri']['month']['ar']
            hijri_month_en = data['data']['date']['hijri']['month']['en']
            hijri_year = data['data']['date']['hijri']['year']
            
            if language == 'ar':
                prayer_text = f"""
🕌 *أوقات الصلاة في {city}*

*التاريخ الميلادي:* {date}
*التاريخ الهجري:* {hijri_day} {hijri_month_ar} {hijri_year} هـ

*الفجر:* {timings['Fajr']}
*الشروق:* {timings['Sunrise']}
*الظهر:* {timings['Dhuhr']}
*العصر:* {timings['Asr']}
*المغرب:* {timings['Maghrib']}
*العشاء:* {timings['Isha']}

*تقبل الله صلاتكم* 🤲
                """
            else:
                prayer_text = f"""
🕌 *Prayer Times for {city}*

*Gregorian Date:* {date}
*Hijri Date:* {hijri_day} {hijri_month_en} {hijri_year} AH

*Fajr:* {timings['Fajr']}
*Sunrise:* {timings['Sunrise']}
*Dhuhr:* {timings['Dhuhr']}
*Asr:* {timings['Asr']}
*Maghrib:* {timings['Maghrib']}
*Isha:* {timings['Isha']}

*May Allah accept your prayers!* 🤲
                """
            return prayer_text
    except Exception as e:
        print(f"API Error: {e}")
    
    # Fallback in both languages
    if language == 'ar':
        return f"""
🕌 *أوقات الصلاة في {city}*

*الفجر:* 5:30 ص
*الشروق:* 7:00 ص  
*الظهر:* 12:30 م
*العصر:* 3:45 م
*المغرب:* 6:15 م
*العشاء:* 7:45 م

*ملاحظة:* استخدام الأوقات التقريبية - جرب مدينة أخرى
        """
    else:
        return f"""
🕌 *Prayer Times for {city}*

*Fajr:* 5:30 AM
*Sunrise:* 7:00 AM  
*Dhuhr:* 12:30 PM
*Asr:* 3:45 PM
*Maghrib:* 6:15 PM
*Isha:* 7:45 PM

*Note:* Using estimated times - Try another city
        """

async def ramadan_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_language = db.get_user_language(update.effective_user.id)
    
    if user_language == 'ar':
        ramadan_text = """
*🌙 معلومات رمضان*

*الأوقات المهمة:*
• السحور ينتهي: 10 دقائق قبل الفجر
• وقت الإفطار: عند المغرب
• صلاة التراويح: بعد صلاة العشاء

*أعمال مستحبة في رمضان:*
- الصدقة والإحسان
- قراءة القرآن الكريم
- قيام الليل
- الاعتكاف في العشر الأواخر

*رمضان مبارك!* 🌙
        """
    else:
        ramadan_text = """
*🌙 Ramadan Information*

*Important Times:*
• Suhur ends: 10 minutes before Fajr
• Iftar time: At Maghrib
• Taraweeh: After Isha prayer

*Recommended Acts in Ramadan:*
- Charity and kindness
- Reading Quran
- Night prayers (Tahajjud)
- I'tikaf in last 10 days

*Ramadan Mubarak!* 🌙
        """
    await update.message.reply_text(ramadan_text)