from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import requests
from database import db
from language import get_text

# Complete Quran Surahs data - ALL 114 SURAHS
QURAN_SURAHS = {
    "1": {"name": "Al-Fatihah", "verses": 7, "revelation": "Meccan"},
    "2": {"name": "Al-Baqarah", "verses": 286, "revelation": "Medinan"},
    "3": {"name": "Ali Imran", "verses": 200, "revelation": "Medinan"},
    "4": {"name": "An-Nisa", "verses": 176, "revelation": "Medinan"},
    "5": {"name": "Al-Ma'idah", "verses": 120, "revelation": "Medinan"},
    "6": {"name": "Al-An'am", "verses": 165, "revelation": "Meccan"},
    "7": {"name": "Al-A'raf", "verses": 206, "revelation": "Meccan"},
    "8": {"name": "Al-Anfal", "verses": 75, "revelation": "Medinan"},
    "9": {"name": "At-Tawbah", "verses": 129, "revelation": "Medinan"},
    "10": {"name": "Yunus", "verses": 109, "revelation": "Meccan"},
    "11": {"name": "Hud", "verses": 123, "revelation": "Meccan"},
    "12": {"name": "Yusuf", "verses": 111, "revelation": "Meccan"},
    "13": {"name": "Ar-Ra'd", "verses": 43, "revelation": "Medinan"},
    "14": {"name": "Ibrahim", "verses": 52, "revelation": "Meccan"},
    "15": {"name": "Al-Hijr", "verses": 99, "revelation": "Meccan"},
    "16": {"name": "An-Nahl", "verses": 128, "revelation": "Meccan"},
    "17": {"name": "Al-Isra", "verses": 111, "revelation": "Meccan"},
    "18": {"name": "Al-Kahf", "verses": 110, "revelation": "Meccan"},
    "19": {"name": "Maryam", "verses": 98, "revelation": "Meccan"},
    "20": {"name": "Taha", "verses": 135, "revelation": "Meccan"},
    "21": {"name": "Al-Anbiya", "verses": 112, "revelation": "Meccan"},
    "22": {"name": "Al-Hajj", "verses": 78, "revelation": "Medinan"},
    "23": {"name": "Al-Mu'minun", "verses": 118, "revelation": "Meccan"},
    "24": {"name": "An-Nur", "verses": 64, "revelation": "Medinan"},
    "25": {"name": "Al-Furqan", "verses": 77, "revelation": "Meccan"},
    "26": {"name": "Ash-Shu'ara", "verses": 227, "revelation": "Meccan"},
    "27": {"name": "An-Naml", "verses": 93, "revelation": "Meccan"},
    "28": {"name": "Al-Qasas", "verses": 88, "revelation": "Meccan"},
    "29": {"name": "Al-Ankabut", "verses": 69, "revelation": "Meccan"},
    "30": {"name": "Ar-Rum", "verses": 60, "revelation": "Meccan"},
    "31": {"name": "Luqman", "verses": 34, "revelation": "Meccan"},
    "32": {"name": "As-Sajdah", "verses": 30, "revelation": "Meccan"},
    "33": {"name": "Al-Ahzab", "verses": 73, "revelation": "Medinan"},
    "34": {"name": "Saba", "verses": 54, "revelation": "Meccan"},
    "35": {"name": "Fatir", "verses": 45, "revelation": "Meccan"},
    "36": {"name": "Ya-Sin", "verses": 83, "revelation": "Meccan"},
    "37": {"name": "As-Saffat", "verses": 182, "revelation": "Meccan"},
    "38": {"name": "Sad", "verses": 88, "revelation": "Meccan"},
    "39": {"name": "Az-Zumar", "verses": 75, "revelation": "Meccan"},
    "40": {"name": "Ghafir", "verses": 85, "revelation": "Meccan"},
    "41": {"name": "Fussilat", "verses": 54, "revelation": "Meccan"},
    "42": {"name": "Ash-Shura", "verses": 53, "revelation": "Meccan"},
    "43": {"name": "Az-Zukhruf", "verses": 89, "revelation": "Meccan"},
    "44": {"name": "Ad-Dukhan", "verses": 59, "revelation": "Meccan"},
    "45": {"name": "Al-Jathiyah", "verses": 37, "revelation": "Meccan"},
    "46": {"name": "Al-Ahqaf", "verses": 35, "revelation": "Meccan"},
    "47": {"name": "Muhammad", "verses": 38, "revelation": "Medinan"},
    "48": {"name": "Al-Fath", "verses": 29, "revelation": "Medinan"},
    "49": {"name": "Al-Hujurat", "verses": 18, "revelation": "Medinan"},
    "50": {"name": "Qaf", "verses": 45, "revelation": "Meccan"},
    "51": {"name": "Adh-Dhariyat", "verses": 60, "revelation": "Meccan"},
    "52": {"name": "At-Tur", "verses": 49, "revelation": "Meccan"},
    "53": {"name": "An-Najm", "verses": 62, "revelation": "Meccan"},
    "54": {"name": "Al-Qamar", "verses": 55, "revelation": "Meccan"},
    "55": {"name": "Ar-Rahman", "verses": 78, "revelation": "Medinan"},
    "56": {"name": "Al-Waqi'ah", "verses": 96, "revelation": "Meccan"},
    "57": {"name": "Al-Hadid", "verses": 29, "revelation": "Medinan"},
    "58": {"name": "Al-Mujadila", "verses": 22, "revelation": "Medinan"},
    "59": {"name": "Al-Hashr", "verses": 24, "revelation": "Medinan"},
    "60": {"name": "Al-Mumtahanah", "verses": 13, "revelation": "Medinan"},
    "61": {"name": "As-Saff", "verses": 14, "revelation": "Medinan"},
    "62": {"name": "Al-Jumu'ah", "verses": 11, "revelation": "Medinan"},
    "63": {"name": "Al-Munafiqun", "verses": 11, "revelation": "Medinan"},
    "64": {"name": "At-Taghabun", "verses": 18, "revelation": "Medinan"},
    "65": {"name": "At-Talaq", "verses": 12, "revelation": "Medinan"},
    "66": {"name": "At-Tahrim", "verses": 12, "revelation": "Medinan"},
    "67": {"name": "Al-Mulk", "verses": 30, "revelation": "Meccan"},
    "68": {"name": "Al-Qalam", "verses": 52, "revelation": "Meccan"},
    "69": {"name": "Al-Haqqah", "verses": 52, "revelation": "Meccan"},
    "70": {"name": "Al-Ma'arij", "verses": 44, "revelation": "Meccan"},
    "71": {"name": "Nuh", "verses": 28, "revelation": "Meccan"},
    "72": {"name": "Al-Jinn", "verses": 28, "revelation": "Meccan"},
    "73": {"name": "Al-Muzzammil", "verses": 20, "revelation": "Meccan"},
    "74": {"name": "Al-Muddathir", "verses": 56, "revelation": "Meccan"},
    "75": {"name": "Al-Qiyamah", "verses": 40, "revelation": "Meccan"},
    "76": {"name": "Al-Insan", "verses": 31, "revelation": "Medinan"},
    "77": {"name": "Al-Mursalat", "verses": 50, "revelation": "Meccan"},
    "78": {"name": "An-Naba", "verses": 40, "revelation": "Meccan"},
    "79": {"name": "An-Nazi'at", "verses": 46, "revelation": "Meccan"},
    "80": {"name": "Abasa", "verses": 42, "revelation": "Meccan"},
    "81": {"name": "At-Takwir", "verses": 29, "revelation": "Meccan"},
    "82": {"name": "Al-Infitar", "verses": 19, "revelation": "Meccan"},
    "83": {"name": "Al-Mutaffifin", "verses": 36, "revelation": "Meccan"},
    "84": {"name": "Al-Inshiqaq", "verses": 25, "revelation": "Meccan"},
    "85": {"name": "Al-Buruj", "verses": 22, "revelation": "Meccan"},
    "86": {"name": "At-Tariq", "verses": 17, "revelation": "Meccan"},
    "87": {"name": "Al-A'la", "verses": 19, "revelation": "Meccan"},
    "88": {"name": "Al-Ghashiyah", "verses": 26, "revelation": "Meccan"},
    "89": {"name": "Al-Fajr", "verses": 30, "revelation": "Meccan"},
    "90": {"name": "Al-Balad", "verses": 20, "revelation": "Meccan"},
    "91": {"name": "Ash-Shams", "verses": 15, "revelation": "Meccan"},
    "92": {"name": "Al-Layl", "verses": 21, "revelation": "Meccan"},
    "93": {"name": "Ad-Duha", "verses": 11, "revelation": "Meccan"},
    "94": {"name": "Ash-Sharh", "verses": 8, "revelation": "Meccan"},
    "95": {"name": "At-Tin", "verses": 8, "revelation": "Meccan"},
    "96": {"name": "Al-Alaq", "verses": 19, "revelation": "Meccan"},
    "97": {"name": "Al-Qadr", "verses": 5, "revelation": "Meccan"},
    "98": {"name": "Al-Bayyinah", "verses": 8, "revelation": "Medinan"},
    "99": {"name": "Az-Zalzalah", "verses": 8, "revelation": "Medinan"},
    "100": {"name": "Al-Adiyat", "verses": 11, "revelation": "Meccan"},
    "101": {"name": "Al-Qari'ah", "verses": 11, "revelation": "Meccan"},
    "102": {"name": "At-Takathur", "verses": 8, "revelation": "Meccan"},
    "103": {"name": "Al-Asr", "verses": 3, "revelation": "Meccan"},
    "104": {"name": "Al-Humazah", "verses": 9, "revelation": "Meccan"},
    "105": {"name": "Al-Fil", "verses": 5, "revelation": "Meccan"},
    "106": {"name": "Quraysh", "verses": 4, "revelation": "Meccan"},
    "107": {"name": "Al-Ma'un", "verses": 7, "revelation": "Meccan"},
    "108": {"name": "Al-Kawthar", "verses": 3, "revelation": "Meccan"},
    "109": {"name": "Al-Kafirun", "verses": 6, "revelation": "Meccan"},
    "110": {"name": "An-Nasr", "verses": 3, "revelation": "Medinan"},
    "111": {"name": "Al-Masad", "verses": 5, "revelation": "Meccan"},
    "112": {"name": "Al-Ikhlas", "verses": 4, "revelation": "Meccan"},
    "113": {"name": "Al-Falaq", "verses": 5, "revelation": "Meccan"},
    "114": {"name": "An-Nas", "verses": 6, "revelation": "Meccan"}
}

async def quran_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    page = int(context.args[0]) if context.args and context.args[0].isdigit() else 1
    await show_surahs_page(update, page)

async def show_surahs_page(update: Update, page: int, message_id=None):
    user_language = db.get_user_language(update.effective_user.id)
    
    surahs_per_page = 20
    start_idx = (page - 1) * surahs_per_page
    end_idx = start_idx + surahs_per_page
    
    surahs_list = list(QURAN_SURAHS.items())[start_idx:end_idx]
    
    keyboard = []
    for surah_num, surah_info in surahs_list:
        keyboard.append([InlineKeyboardButton(
            f"{surah_num}. {surah_info['name']} ({surah_info['verses']} verses)",
            callback_data=f"surah_{surah_num}_page_1"
        )])
    
    # Navigation buttons with language support
    nav_buttons = []
    if page > 1:
        if user_language == 'ar':
            nav_buttons.append(InlineKeyboardButton("⬅️ السابق", callback_data=f"quran_page_{page-1}"))
        else:
            nav_buttons.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"quran_page_{page-1}"))
    
    total_pages = (len(QURAN_SURAHS) - 1) // surahs_per_page + 1
    nav_buttons.append(InlineKeyboardButton(f"{page}/{total_pages}", callback_data="noop"))
    
    if end_idx < len(QURAN_SURAHS):
        if user_language == 'ar':
            nav_buttons.append(InlineKeyboardButton("التالي ➡️", callback_data=f"quran_page_{page+1}"))
        else:
            nav_buttons.append(InlineKeyboardButton("Next ➡️", callback_data=f"quran_page_{page+1}"))
    
    if nav_buttons:
        keyboard.append(nav_buttons)
    
    if user_language == 'ar':
        keyboard.append([InlineKeyboardButton("↩️ العودة للرئيسية", callback_data="back_main")])
        text = f"📖 *اختر سورة (الصفحة {page}):*"
    else:
        keyboard.append([InlineKeyboardButton("↩️ Back to Main", callback_data="back_main")])
        text = f"📖 *Select a Surah (Page {page}):*"
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if message_id:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(text, reply_markup=reply_markup)

async def show_surah_page(update: Update, surah_num: str, page: int):
    query = update.callback_query
    await query.answer()
    
    user_language = db.get_user_language(update.effective_user.id)
    surah_info = QURAN_SURAHS.get(surah_num)
    if not surah_info:
        if user_language == 'ar':
            await query.edit_message_text("❌ السورة غير موجودة.")
        else:
            await query.edit_message_text("❌ Surah not found.")
        return
    
    verses_per_page = 5
    start_verse = (page - 1) * verses_per_page + 1
    end_verse = min(page * verses_per_page, surah_info['verses'])
    
    # Build the message for current page
    if user_language == 'ar':
        message_text = f"🕌 *سورة {surah_info['name']}* ({surah_num})\n"
        message_text += f"*الآيات {start_verse}-{end_verse} من {surah_info['verses']}* | {surah_info['revelation']}\n\n"
    else:
        message_text = f"🕌 *Surah {surah_info['name']}* ({surah_num})\n"
        message_text += f"*Verses {start_verse}-{end_verse} of {surah_info['verses']}* | {surah_info['revelation']}\n\n"
    
    # Get verses for current page
    for verse_num in range(start_verse, end_verse + 1):
        verse_text = await get_quran_verse_compact(surah_num, str(verse_num))
        if verse_text:
            message_text += verse_text + "\n"
    
    # Check message length and truncate if necessary
    if len(message_text) > 4000:
        message_text = message_text[:4000] + "\n\n... (message truncated)"
    
    # Build navigation keyboard
    keyboard = []
    
    # Verse navigation (Previous/Next)
    nav_buttons = []
    if page > 1:
        if user_language == 'ar':
            nav_buttons.append(InlineKeyboardButton("⬅️ السابق", callback_data=f"surah_{surah_num}_page_{page-1}"))
        else:
            nav_buttons.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"surah_{surah_num}_page_{page-1}"))
    
    # Show current page info
    total_pages = (surah_info['verses'] - 1) // verses_per_page + 1
    nav_buttons.append(InlineKeyboardButton(f"{page}/{total_pages}", callback_data="noop"))
    
    if end_verse < surah_info['verses']:
        if user_language == 'ar':
            nav_buttons.append(InlineKeyboardButton("التالي ➡️", callback_data=f"surah_{surah_num}_page_{page+1}"))
        else:
            nav_buttons.append(InlineKeyboardButton("Next ➡️", callback_data=f"surah_{surah_num}_page_{page+1}"))
    
    if nav_buttons:
        keyboard.append(nav_buttons)
    
    # Additional actions
    action_buttons = []
    if surah_info['verses'] > 10:
        if user_language == 'ar':
            action_buttons.append(InlineKeyboardButton("🔍 الانتقال إلى قسم", callback_data=f"jump_{surah_num}"))
        else:
            action_buttons.append(InlineKeyboardButton("🔍 Jump to Section", callback_data=f"jump_{surah_num}"))
    
    if user_language == 'ar':
        action_buttons.append(InlineKeyboardButton("📖 جميع السور", callback_data="quran_page_1"))
    else:
        action_buttons.append(InlineKeyboardButton("📖 All Surahs", callback_data="quran_page_1"))
    
    if action_buttons:
        keyboard.append(action_buttons)
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        await query.edit_message_text(message_text, reply_markup=reply_markup)
    except Exception as e:
        # If still too long, send as new message
        await query.message.reply_text(message_text, reply_markup=reply_markup)

# NEW COMPACT VERSE FORMAT
async def get_quran_verse_compact(surah: str, verse: str):
    try:
        url = f"http://api.alquran.cloud/v1/ayah/{surah}:{verse}/editions/quran-uthmani,en.asad"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if data['code'] == 200:
            arabic = data['data'][0]['text']
            english = data['data'][1]['text']
            
            # Compact format to save space
            return f"**{verse}.** {arabic}\n{english}\n─"
    except Exception as e:
        print(f"Error fetching verse: {e}")
    
    # Fallback compact format
    return f"**{verse}.** بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ\nIn the name of Allah.\n─"

async def surah_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_language = db.get_user_language(update.effective_user.id)
    
    if not context.args:
        if user_language == 'ar':
            await update.message.reply_text("الرجاء تحديد رقم السورة: `/surah 1`")
        else:
            await update.message.reply_text("Please specify a Surah number: `/surah 1`")
        return
    
    surah_num = context.args[0]
    if surah_num in QURAN_SURAHS:
        # Create a mock callback query for direct command usage
        mock_update = type('Update', (), {})()
        mock_update.callback_query = type('CallbackQuery', (), {})()
        mock_update.callback_query.message = update.message
        mock_update.callback_query.edit_message_text = update.message.reply_text
        mock_update.callback_query.answer = lambda: None
        await show_surah_page(mock_update, surah_num, 1)
    else:
        if user_language == 'ar':
            await update.message.reply_text("❌ السورة غير موجودة. استخدم `/quran` لرؤية جميع السور.")
        else:
            await update.message.reply_text("❌ Surah not found. Use `/quran` to see all Surahs.")

async def handle_jump_to_verse(update: Update, surah_num: str):
    query = update.callback_query
    await query.answer()
    
    user_language = db.get_user_language(update.effective_user.id)
    surah_info = QURAN_SURAHS.get(surah_num)
    if not surah_info:
        return
    
    # Create keyboard with verse ranges for quick jumping (5 verses per page now)
    keyboard = []
    verses = surah_info['verses']
    
    # Create buttons for every 25 verses (5 verses per page × 5 pages per button)
    for start in range(1, verses + 1, 25):
        end = min(start + 24, verses)
        if user_language == 'ar':
            keyboard.append([InlineKeyboardButton(
                f"الآيات {start}-{end}",
                callback_data=f"surah_{surah_num}_page_{((start-1)//5)+1}"
            )])
        else:
            keyboard.append([InlineKeyboardButton(
                f"Verses {start}-{end}",
                callback_data=f"surah_{surah_num}_page_{((start-1)//5)+1}"
            )])
    
    if user_language == 'ar':
        keyboard.append([InlineKeyboardButton("↩️ العودة", callback_data=f"surah_{surah_num}_page_1")])
    else:
        keyboard.append([InlineKeyboardButton("↩️ Back", callback_data=f"surah_{surah_num}_page_1")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if user_language == 'ar':
        await query.edit_message_text(
            f"🔍 *الانتقال إلى قسم في سورة {surah_info['name']}:*",
            reply_markup=reply_markup
        )
    else:
        await query.edit_message_text(
            f"🔍 *Jump to section in Surah {surah_info['name']}:*",
            reply_markup=reply_markup
        )