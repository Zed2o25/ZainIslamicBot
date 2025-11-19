from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import requests
import math
from datetime import datetime
from database import db

async def tools_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_language = db.get_user_language(update.effective_user.id)
    
    if user_language == 'ar':
        text = """
🕋 *الأدوات الإسلامية*

اختر الأداة التي تريد استخدامها:

*القبلة* - اتجاه القبلة من موقعك
*التقويم* - التاريخ الهجري والميلادي  
*الزكاة* - حاسبة زكاة المال
*الصلوات* - أوقات الصلاة
        """
        
        keyboard = [
            [InlineKeyboardButton("🕋 اتجاه القبلة", callback_data="qibla_tool"),
             InlineKeyboardButton("📅 التقويم الإسلامي", callback_data="calendar_tool")],
            [InlineKeyboardButton("💰 حاسبة الزكاة", callback_data="zakat_tool")],
            [InlineKeyboardButton("🕌 أوقات الصلاة", callback_data="prayer")],
            [InlineKeyboardButton("↩️ العودة للرئيسية", callback_data="back_main")]
        ]
    else:
        text = """
🕋 *Islamic Tools*

Select the tool you want to use:

*Qibla* - Qibla direction from your location
*Calendar* - Hijri and Gregorian dates
*Zakat* - Zakat calculator for your wealth  
*Prayers* - Prayer times
        """
        
        keyboard = [
            [InlineKeyboardButton("🕋 Qibla Direction", callback_data="qibla_tool"),
             InlineKeyboardButton("📅 Islamic Calendar", callback_data="calendar_tool")],
            [InlineKeyboardButton("💰 Zakat Calculator", callback_data="zakat_tool")],
            [InlineKeyboardButton("🕌 Prayer Times", callback_data="prayer")],
            [InlineKeyboardButton("↩️ Back to Main", callback_data="back_main")]
        ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if hasattr(update, 'callback_query') and update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(text, reply_markup=reply_markup)

async def qibla_tool(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_language = db.get_user_language(update.effective_user.id)
    
    if user_language == 'ar':
        text = """
🕋 *اتجاه القبلة*

أدخل اسم مدينتك لمعرفة اتجاه القبلة:

مثال:
`مكة`
`الرياض` 
`دبي`
`القاهرة`

أو انقر على الزر أدناه لإدخال المدينة
        """
        
        keyboard = [
            [InlineKeyboardButton("🏙️ أدخل اسم المدينة", callback_data="enter_city")],
            [InlineKeyboardButton("↩️ العودة", callback_data="tools_main")]
        ]
    else:
        text = """
🕋 *Qibla Direction*

Enter your city name to find Qibla direction:

Examples:
`Mecca`
`Riyadh`
`Dubai` 
`Cairo`

Or click the button below to enter city
        """
        
        keyboard = [
            [InlineKeyboardButton("🏙️ Enter City Name", callback_data="enter_city")],
            [InlineKeyboardButton("↩️ Back", callback_data="tools_main")]
        ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if hasattr(update, 'callback_query') and update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(text, reply_markup=reply_markup)

async def get_qibla_direction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_language = db.get_user_language(update.effective_user.id)
    
    # Get city from command arguments
    if context.args:
        city = " ".join(context.args)
    else:
        city = "Mecca"  # Default city
    
    try:
        # Qibla directions for major cities
        qibla_directions = {
            'mecca': {'ar': 'في اتجاه الكعبة', 'en': 'Towards Kaaba'},
            'makkah': {'ar': 'في اتجاه الكعبة', 'en': 'Towards Kaaba'},
            'riyadh': {'ar': 'غرب', 'en': 'West'},
            'dubai': {'ar': 'غرب', 'en': 'West'}, 
            'cairo': {'ar': 'جنوب شرق', 'en': 'Southeast'},
            'istanbul': {'ar': 'جنوب شرق', 'en': 'Southeast'},
            'london': {'ar': 'جنوب شرق', 'en': 'Southeast'},
            'new york': {'ar': 'شمال شرق', 'en': 'Northeast'},
            'paris': {'ar': 'جنوب شرق', 'en': 'Southeast'},
            'berlin': {'ar': 'جنوب شرق', 'en': 'Southeast'},
            'moscow': {'ar': 'جنوب', 'en': 'South'},
            'tokyo': {'ar': 'غرب', 'en': 'West'},
            'singapore': {'ar': 'شمال غرب', 'en': 'Northwest'},
            'sydney': {'ar': 'شمال غرب', 'en': 'Northwest'},
            'jeddah': {'ar': 'شرق', 'en': 'East'},
            'medina': {'ar': 'جنوب', 'en': 'South'}
        }
        
        city_lower = city.lower()
        direction = None
        
        for key, value in qibla_directions.items():
            if key in city_lower:
                direction = value
                break
        
        if not direction:
            direction = {'ar': 'غرب', 'en': 'West'}  # Default direction
        
        if user_language == 'ar':
            result = f"""
🕋 *اتجاه القبلة لـ {city}*

*الاتجاه:* {direction['ar']}

*توجيه:*
- استخدم بوصلة الهاتف
- توجه نحو {direction['ar']}
- الكعبة في مكة المكرمة

*تقبل الله طاعاتك* 🕋
            """
        else:
            result = f"""
🕋 *Qibla Direction for {city}*

*Direction:* {direction['en']}

*Instructions:*
- Use your phone's compass  
- Face towards {direction['en']}
- Kaaba is in Mecca

*May Allah accept your prayers* 🕋
            """
        
        await update.message.reply_text(result)
                
    except Exception as e:
        print(f"Qibla error: {e}")
        if user_language == 'ar':
            await update.message.reply_text("❌ حدث خطأ في حساب اتجاه القبلة. حاول مرة أخرى.")
        else:
            await update.message.reply_text("❌ Error calculating Qibla direction. Please try again.")

async def calendar_tool(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_language = db.get_user_language(update.effective_user.id)
    
    try:
        # Get current date
        today = datetime.now()
        gregorian_date = today.strftime("%A, %B %d, %Y")
        
        # Simple Hijri date calculation (approximate)
        hijri_months_ar = [
            "محرم", "صفر", "ربيع الأول", "ربيع الثاني", 
            "جمادى الأولى", "جمادى الآخرة", "رجب", "شعبان", 
            "رمضان", "شوال", "ذو القعدة", "ذو الحجة"
        ]
        
        hijri_months_en = [
            "Muharram", "Safar", "Rabi al-Awwal", "Rabi al-Thani",
            "Jumada al-Awwal", "Jumada al-Thani", "Rajab", "Sha'ban",
            "Ramadan", "Shawwal", "Dhu al-Qidah", "Dhu al-Hijjah"
        ]
        
        # Approximate conversion (this is simplified)
        hijri_year = 1446  # Approximate current Hijri year
        hijri_month = (today.month + 8) % 12
        hijri_day = today.day
        
        month_name_ar = hijri_months_ar[hijri_month]
        month_name_en = hijri_months_en[hijri_month]
        
        if user_language == 'ar':
            text = f"""
📅 *التقويم الإسلامي*

*التاريخ الميلادي:*
{gregorian_date}

*التاريخ الهجري (تقريبي):*
{month_name_ar} {hijri_day}, {hijri_year} هـ

*أهم الأحداث:*
- رمضان: 9 هـ
- الحج: 12 هـ
- رأس السنة: 1 محرم

*تقبل الله طاعاتك* 📅
            """
        else:
            text = f"""
📅 *Islamic Calendar*

*Gregorian Date:*
{gregorian_date}

*Hijri Date (Approximate):*
{month_name_en} {hijri_day}, {hijri_year} AH

*Important Events:*
- Ramadan: 9th month
- Hajj: 12th month
- Islamic New Year: 1st Muharram

*May Allah accept your deeds* 📅
            """
        
        keyboard = [
            [InlineKeyboardButton("🔄 تحديث", callback_data="calendar_tool")],
            [InlineKeyboardButton("↩️ العودة", callback_data="tools_main")]
        ] if user_language == 'ar' else [
            [InlineKeyboardButton("🔄 Refresh", callback_data="calendar_tool")],
            [InlineKeyboardButton("↩️ Back", callback_data="tools_main")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if hasattr(update, 'callback_query') and update.callback_query:
            await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
        else:
            await update.message.reply_text(text, reply_markup=reply_markup)
            
    except Exception as e:
        if user_language == 'ar':
            await update.message.reply_text("❌ حدث خطأ في عرض التقويم. حاول مرة أخرى.")
        else:
            await update.message.reply_text("❌ Error displaying calendar. Please try again.")

async def zakat_tool(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_language = db.get_user_language(update.effective_user.id)
    
    if user_language == 'ar':
        text = """
💰 *حاسبة الزكاة*

أدخل قيمة أموالك بالعملة المحلية:

مثال:
`/zakat 5000` - لحساب زكاة 5000 وحدة نقدية

*شروط الزكاة:*
- بلوغ النصاب (85 جرام ذهب)
- مرور سنة هجرية
- الملكية التامة

*نصاب الزكاة:* 2.5% من إجمالي المدخرات
        """
        
        keyboard = [
            [InlineKeyboardButton("💵 حساب الزكاة", callback_data="calculate_zakat")],
            [InlineKeyboardButton("📊 دليل الزكاة", callback_data="zakat_guide")],
            [InlineKeyboardButton("↩️ العودة", callback_data="tools_main")]
        ]
    else:
        text = """
💰 *Zakat Calculator*

Enter your wealth amount in local currency:

Example:
`/zakat 5000` - to calculate Zakat for 5000 currency units

*Zakat Conditions:*
- Reach Nisab (85g gold)
- Pass one lunar year
- Full ownership

*Zakat Rate:* 2.5% of total savings
        """
        
        keyboard = [
            [InlineKeyboardButton("💵 Calculate Zakat", callback_data="calculate_zakat")],
            [InlineKeyboardButton("📊 Zakat Guide", callback_data="zakat_guide")],
            [InlineKeyboardButton("↩️ Back", callback_data="tools_main")]
        ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if hasattr(update, 'callback_query') and update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(text, reply_markup=reply_markup)

async def calculate_zakat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_language = db.get_user_language(update.effective_user.id)
    
    if not context.args:
        if user_language == 'ar':
            await update.message.reply_text("❌ الرجاء إدخال المبلغ. مثال: `/zakat 5000`")
        else:
            await update.message.reply_text("❌ Please enter the amount. Example: `/zakat 5000`")
        return
    
    try:
        amount = float(context.args[0])
        zakat_amount = amount * 0.025  # 2.5%
        nisab_gold = 85  # grams of gold
        nisab_value = 5000  # approximate value in local currency
        
        if amount < nisab_value:
            if user_language == 'ar':
                result = f"""
💰 *نتيجة حساب الزكاة*

*المبلغ المدخل:* {amount:,.2f}
*نصاب الزكاة:* {nisab_value:,.2f}

*النتيجة:* المبلغ أقل من النصاب
*لا تجب الزكاة على هذا المبلغ*

*ملاحظة:* النصاب يعادل {nisab_gold} جرام ذهب
                """
            else:
                result = f"""
💰 *Zakat Calculation Result*

*Entered Amount:* {amount:,.2f}
*Nisab Threshold:* {nisab_value:,.2f}

*Result:* Amount is below Nisab
*Zakat is not obligatory on this amount*

*Note:* Nisab is equivalent to {nisab_gold}g of gold
                """
        else:
            if user_language == 'ar':
                result = f"""
💰 *نتيجة حساب الزكاة*

*المبلغ المدخل:* {amount:,.2f}
*نصاب الزكاة:* {nisab_value:,.2f}

*زكاة المال المستحقة:* {zakat_amount:,.2f}
*النسبة:* 2.5%

*توجيهات:*
- ادفع الزكاة للمستحقين
- يمكن تقسيمها على عدة فقراء
- الأفضل إخراجها في رمضان

*تقبل الله منك* 🤲
                """
            else:
                result = f"""
💰 *Zakat Calculation Result*

*Entered Amount:* {amount:,.2f}
*Nisab Threshold:* {nisab_value:,.2f}

*Zakat Due:* {zakat_amount:,.2f}
*Rate:* 2.5%

*Instructions:*
- Pay Zakat to eligible recipients
- Can be distributed to multiple poor people
- Best to pay during Ramadan

*May Allah accept from you* 🤲
                """
        
        await update.message.reply_text(result)
        
    except ValueError:
        if user_language == 'ar':
            await update.message.reply_text("❌ الرجاء إدخال رقم صحيح. مثال: `/zakat 5000`")
        else:
            await update.message.reply_text("❌ Please enter a valid number. Example: `/zakat 5000`")

async def zakat_guide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_language = db.get_user_language(update.effective_user.id)
    
    if user_language == 'ar':
        guide = """
📚 *دليل الزكاة*

*شروط وجوب الزكاة:*
1. الإسلام
2. الحرية
3. ملك النصاب
4. مرور الحول
5. الملك التام

*أصناف الزكاة:*
- الأموال النقدية
- الذهب والفضة
- عروض التجارة
- الزروع والثمار
- الأنعام

*مصارف الزكاة (8 أصناف):*
1. الفقراء
2. المساكين
3. العاملون عليها
4. المؤلفة قلوبهم
5. في الرقاب
6. الغارمون
7. في سبيل الله
8. ابن السبيل

*نصاب الذهب:* 85 جرام
*نصاب الفضة:* 595 جرام
*معدل الزكاة:* 2.5%
        """
    else:
        guide = """
📚 *Zakat Guide*

*Conditions for Zakat:*
1. Muslim
2. Free person
3. Ownership of Nisab
4. Completion of lunar year
5. Full ownership

*Types of Wealth for Zakat:*
- Cash money
- Gold and silver
- Trade goods
- Agricultural produce
- Livestock

*Recipients of Zakat (8 categories):*
1. The poor
2. The needy
3. Zakat administrators
4. Those whose hearts are to be reconciled
5. Those in bondage
6. The debt-ridden
7. In the cause of Allah
8. The wayfarer

*Gold Nisab:* 85 grams
*Silver Nisab:* 595 grams
*Zakat Rate:* 2.5%
        """
    
    await update.message.reply_text(guide)