from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import random
from database import db
from language import get_text

# Enhanced Hadith Collection
HADITH_COLLECTION = [
    {
        "text": "The Prophet (ﷺ) said: 'The most perfect believer in faith is the one who is best in moral character...'",
        "source": "Sunan al-Tirmidhi",
        "number": "1162"
    },
    {
        "text": "The Prophet (ﷺ) said: 'None of you truly believes until he loves for his brother what he loves for himself.'",
        "source": "Sahih al-Bukhari", 
        "number": "13"
    },
    {
        "text": "The Prophet (ﷺ) said: 'A good word is charity.'",
        "source": "Sahih al-Bukhari",
        "number": "2989"
    },
    {
        "text": "The Prophet (ﷺ) said: 'The strong believer is better and more beloved to Allah than the weak believer...'",
        "source": "Sahih Muslim",
        "number": "2664"
    },
    {
        "text": "The Prophet (ﷺ) said: 'Cleanliness is half of faith.'",
        "source": "Sahih Muslim", 
        "number": "223"
    },
    {
        "text": "The Prophet (ﷺ) said: 'The best among you are those who have the best manners and character.'",
        "source": "Sahih al-Bukhari",
        "number": "6029"
    },
    {
        "text": "The Prophet (ﷺ) said: 'Seek knowledge from the cradle to the grave.'",
        "source": "Al-Bayhaqi",
        "number": "1.191"
    },
    {
        "text": "The Prophet (ﷺ) said: 'The ink of the scholar is more sacred than the blood of the martyr.'",
        "source": "Sunan Ibn Majah",
        "number": "223"
    }
]

# COMPLETE 99 Names of Allah
ALLAH_NAMES_FULL = [
    {"number": 1, "arabic": "الرَّحْمَٰنُ", "transliteration": "Ar-Rahman", "meaning": "The Beneficent"},
    {"number": 2, "arabic": "الرَّحِيمُ", "transliteration": "Ar-Raheem", "meaning": "The Merciful"},
    {"number": 3, "arabic": "الْمَلِكُ", "transliteration": "Al-Malik", "meaning": "The Eternal Lord"},
    {"number": 4, "arabic": "الْقُدُّوسُ", "transliteration": "Al-Quddus", "meaning": "The Most Sacred"},
    {"number": 5, "arabic": "السَّلَامُ", "transliteration": "As-Salam", "meaning": "The Embodiment of Peace"},
    {"number": 6, "arabic": "الْمُؤْمِنُ", "transliteration": "Al-Mu'min", "meaning": "The Infuser of Faith"},
    {"number": 7, "arabic": "الْمُهَيْمِنُ", "transliteration": "Al-Muhaymin", "meaning": "The Preserver of Safety"},
    {"number": 8, "arabic": "الْعَزِيزُ", "transliteration": "Al-Aziz", "meaning": "The Mighty One"},
    {"number": 9, "arabic": "الْجَبَّارُ", "transliteration": "Al-Jabbar", "meaning": "The Compeller"},
    {"number": 10, "arabic": "الْمُتَكَبِّرُ", "transliteration": "Al-Mutakabbir", "meaning": "The Supreme One"},
    {"number": 11, "arabic": "الْخَالِقُ", "transliteration": "Al-Khaliq", "meaning": "The Creator"},
    {"number": 12, "arabic": "الْبَارِئُ", "transliteration": "Al-Bari", "meaning": "The Evolver"},
    {"number": 13, "arabic": "الْمُصَوِّرُ", "transliteration": "Al-Musawwir", "meaning": "The Fashioner"},
    {"number": 14, "arabic": "الْغَفَّارُ", "transliteration": "Al-Ghaffar", "meaning": "The Great Forgiver"},
    {"number": 15, "arabic": "الْقَهَّارُ", "transliteration": "Al-Qahhar", "meaning": "The All-Prevailing One"},
    {"number": 16, "arabic": "الْوَهَّابُ", "transliteration": "Al-Wahhab", "meaning": "The Bestower"},
    {"number": 17, "arabic": "الرَّزَّاقُ", "transliteration": "Ar-Razzaq", "meaning": "The Provider"},
    {"number": 18, "arabic": "الْفَتَّاحُ", "transliteration": "Al-Fattah", "meaning": "The Supreme Solver"},
    {"number": 19, "arabic": "اَلْعَلِيْمُ", "transliteration": "Al-Alim", "meaning": "The All-Knowing"},
    {"number": 20, "arabic": "الْقَابِضُ", "transliteration": "Al-Qabid", "meaning": "The Withholder"},
    {"number": 21, "arabic": "الْبَاسِطُ", "transliteration": "Al-Basit", "meaning": "The Extender"},
    {"number": 22, "arabic": "الْخَافِضُ", "transliteration": "Al-Khafid", "meaning": "The Reducer"},
    {"number": 23, "arabic": "الرَّافِعُ", "transliteration": "Ar-Rafi", "meaning": "The Exalter"},
    {"number": 24, "arabic": "المُعِزُّ", "transliteration": "Al-Mu'izz", "meaning": "The Honourer"},
    {"number": 25, "arabic": "المُذِلُّ", "transliteration": "Al-Mudhill", "meaning": "The Dishonourer"},
    {"number": 26, "arabic": "السَّمِيعُ", "transliteration": "As-Sami", "meaning": "The All-Hearing"},
    {"number": 27, "arabic": "الْبَصِيرُ", "transliteration": "Al-Basir", "meaning": "The All-Seeing"},
    {"number": 28, "arabic": "الْحَكَمُ", "transliteration": "Al-Hakam", "meaning": "The Impartial Judge"},
    {"number": 29, "arabic": "الْعَدْلُ", "transliteration": "Al-Adl", "meaning": "The Embodiment of Justice"},
    {"number": 30, "arabic": "اللَّطِيفُ", "transliteration": "Al-Latif", "meaning": "The Knower of Subtleties"},
    {"number": 31, "arabic": "الْخَبِيرُ", "transliteration": "Al-Khabir", "meaning": "The All-Aware"},
    {"number": 32, "arabic": "الْحَلِيمُ", "transliteration": "Al-Halim", "meaning": "The Clement"},
    {"number": 33, "arabic": "الْعَظِيمُ", "transliteration": "Al-Azim", "meaning": "The Magnificent"},
    {"number": 34, "arabic": "الْغَفُورُ", "transliteration": "Al-Ghafur", "meaning": "The All-Forgiving"},
    {"number": 35, "arabic": "الشَّكُورُ", "transliteration": "Ash-Shakur", "meaning": "The Grateful"},
    {"number": 36, "arabic": "الْعَلِيُّ", "transliteration": "Al-Ali", "meaning": "The Sublime"},
    {"number": 37, "arabic": "الْكَبِيرُ", "transliteration": "Al-Kabir", "meaning": "The Great"},
    {"number": 38, "arabic": "الْحَفِيظُ", "transliteration": "Al-Hafiz", "meaning": "The Preserver"},
    {"number": 39, "arabic": "المُقِيتُ", "transliteration": "Al-Muqit", "meaning": "The Nourisher"},
    {"number": 40, "arabic": "الْحَسِيبُ", "transliteration": "Al-Hasib", "meaning": "The Reckoner"},
    {"number": 41, "arabic": "الْجَلِيلُ", "transliteration": "Al-Jalil", "meaning": "The Majestic"},
    {"number": 42, "arabic": "الْكَرِيمُ", "transliteration": "Al-Karim", "meaning": "The Generous"},
    {"number": 43, "arabic": "الرَّقِيبُ", "transliteration": "Ar-Raqib", "meaning": "The Watchful"},
    {"number": 44, "arabic": "المُجِيبُ", "transliteration": "Al-Mujib", "meaning": "The Responsive"},
    {"number": 45, "arabic": "الْوَاسِعُ", "transliteration": "Al-Wasi", "meaning": "The All-Encompassing"},
    {"number": 46, "arabic": "الْحَكِيمُ", "transliteration": "Al-Hakim", "meaning": "The Wise"},
    {"number": 47, "arabic": "الْوَدُودُ", "transliteration": "Al-Wadud", "meaning": "The Loving"},
    {"number": 48, "arabic": "الْمَجِيدُ", "transliteration": "Al-Majid", "meaning": "The Glorious"},
    {"number": 49, "arabic": "الْبَاعِثُ", "transliteration": "Al-Ba'ith", "meaning": "The Resurrector"},
    {"number": 50, "arabic": "الشَّهِيدُ", "transliteration": "Ash-Shahid", "meaning": "The Witness"},
    {"number": 51, "arabic": "الْحَقُّ", "transliteration": "Al-Haqq", "meaning": "The Truth"},
    {"number": 52, "arabic": "الْوَكِيلُ", "transliteration": "Al-Wakil", "meaning": "The Trustee"},
    {"number": 53, "arabic": "الْقَوِيُّ", "transliteration": "Al-Qawiy", "meaning": "The Strong"},
    {"number": 54, "arabic": "الْمَتِينُ", "transliteration": "Al-Matin", "meaning": "The Firm"},
    {"number": 55, "arabic": "الْوَلِيُّ", "transliteration": "Al-Wali", "meaning": "The Protector"},
    {"number": 56, "arabic": "الْحَمِيدُ", "transliteration": "Al-Hamid", "meaning": "The Praiseworthy"},
    {"number": 57, "arabic": "الْمُحْصِي", "transliteration": "Al-Muhsi", "meaning": "The Accounter"},
    {"number": 58, "arabic": "الْمُبْدِئُ", "transliteration": "Al-Mubdi", "meaning": "The Originator"},
    {"number": 59, "arabic": "الْمُعِيدُ", "transliteration": "Al-Mu'id", "meaning": "The Restorer"},
    {"number": 60, "arabic": "الْمُحْيِي", "transliteration": "Al-Muhyi", "meaning": "The Giver of Life"},
    {"number": 61, "arabic": "الْمُمِيتُ", "transliteration": "Al-Mumit", "meaning": "The Bringer of Death"},
    {"number": 62, "arabic": "الْحَيُّ", "transliteration": "Al-Hayy", "meaning": "The Ever-Living"},
    {"number": 63, "arabic": "الْقَيُّومُ", "transliteration": "Al-Qayyum", "meaning": "The Self-Subsisting"},
    {"number": 64, "arabic": "الْوَاجِدُ", "transliteration": "Al-Wajid", "meaning": "The Perceiver"},
    {"number": 65, "arabic": "الْمَاجِدُ", "transliteration": "Al-Majid", "meaning": "The Illustrious"},
    {"number": 66, "arabic": "الْوَاحِدُ", "transliteration": "Al-Wahid", "meaning": "The Unique"},
    {"number": 67, "arabic": "الْأَحَد", "transliteration": "Al-Ahad", "meaning": "The One"},
    {"number": 68, "arabic": "الصَّمَدُ", "transliteration": "As-Samad", "meaning": "The Eternal"},
    {"number": 69, "arabic": "الْقَادِرُ", "transliteration": "Al-Qadir", "meaning": "The Omnipotent"},
    {"number": 70, "arabic": "الْمُقْتَدِرُ", "transliteration": "Al-Muqtadir", "meaning": "The Powerful"},
    {"number": 71, "arabic": "الْمُقَدِّمُ", "transliteration": "Al-Muqaddim", "meaning": "The Expediter"},
    {"number": 72, "arabic": "الْمُؤَخِّرُ", "transliteration": "Al-Mu'akhkhir", "meaning": "The Delayer"},
    {"number": 73, "arabic": "الْأَوَّلُ", "transliteration": "Al-Awwal", "meaning": "The First"},
    {"number": 74, "arabic": "الْآخِرُ", "transliteration": "Al-Akhir", "meaning": "The Last"},
    {"number": 75, "arabic": "الظَّاهِرُ", "transliteration": "Az-Zahir", "meaning": "The Manifest"},
    {"number": 76, "arabic": "الْبَاطِنُ", "transliteration": "Al-Batin", "meaning": "The Hidden"},
    {"number": 77, "arabic": "الْوَالِي", "transliteration": "Al-Wali", "meaning": "The Governor"},
    {"number": 78, "arabic": "الْمُتَعَالِي", "transliteration": "Al-Muta'ali", "meaning": "The Exalted"},
    {"number": 79, "arabic": "الْبَرُّ", "transliteration": "Al-Barr", "meaning": "The Source of Goodness"},
    {"number": 80, "arabic": "التَّوَّابُ", "transliteration": "At-Tawwab", "meaning": "The Acceptor of Repentance"},
    {"number": 81, "arabic": "الْمُنْتَقِمُ", "transliteration": "Al-Muntaqim", "meaning": "The Avenger"},
    {"number": 82, "arabic": "العَفُوُّ", "transliteration": "Al-Afuw", "meaning": "The Pardoner"},
    {"number": 83, "arabic": "الرَّءُوفُ", "transliteration": "Ar-Ra'uf", "meaning": "The Compassionate"},
    {"number": 84, "arabic": "مَالِكُ الْمُلْكِ", "transliteration": "Malikul-Mulk", "meaning": "The Owner of Sovereignty"},
    {"number": 85, "arabic": "ذُو الْجَلَالِ وَالْإِكْرَامِ", "transliteration": "Dhu-al-Jalal wa-al-Ikram", "meaning": "The Lord of Majesty and Bounty"},
    {"number": 86, "arabic": "الْمُقْسِطُ", "transliteration": "Al-Muqsit", "meaning": "The Equitable"},
    {"number": 87, "arabic": "الْجَامِعُ", "transliteration": "Al-Jami", "meaning": "The Gatherer"},
    {"number": 88, "arabic": "الْغَنِيُّ", "transliteration": "Al-Ghani", "meaning": "The Self-Sufficient"},
    {"number": 89, "arabic": "المُغْنِي", "transliteration": "Al-Mughni", "meaning": "The Enricher"},
    {"number": 90, "arabic": "اَلْمَانِعُ", "transliteration": "Al-Mani", "meaning": "The Preventer"},
    {"number": 91, "arabic": "الضَّارُ", "transliteration": "Ad-Darr", "meaning": "The Distresser"},
    {"number": 92, "arabic": "النَّافِعُ", "transliteration": "An-Nafi", "meaning": "The Propitious"},
    {"number": 93, "arabic": "النُّورُ", "transliteration": "An-Nur", "meaning": "The Light"},
    {"number": 94, "arabic": "الْهَادِي", "transliteration": "Al-Hadi", "meaning": "The Guide"},
    {"number": 95, "arabic": "الْبَدِيعُ", "transliteration": "Al-Badi", "meaning": "The Incomparable"},
    {"number": 96, "arabic": "الْبَاقِي", "transliteration": "Al-Baqi", "meaning": "The Everlasting"},
    {"number": 97, "arabic": "الْوَارِثُ", "transliteration": "Al-Warith", "meaning": "The Inheritor"},
    {"number": 98, "arabic": "الرَّشِيدُ", "transliteration": "Ar-Rashid", "meaning": "The Guide to the Right Path"},
    {"number": 99, "arabic": "الصَّبُورُ", "transliteration": "As-Sabur", "meaning": "The Patient"}
]

async def hadith_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_language = db.get_user_language(update.effective_user.id)
    hadith = random.choice(HADITH_COLLECTION)
    
    if user_language == 'ar':
        hadith_text = f"""
📚 *حديث اليوم*

{hadith['text']}

*المصدر:* {hadith['source']}
*الرقم:* {hadith['number']}

*نسأل الله أن ينفعنا بهذه الأحاديث* 🤲
        """
    else:
        hadith_text = f"""
📚 *Hadith of the Day*

{hadith['text']}

*Source:* {hadith['source']}
*Number:* {hadith['number']}

*May we benefit from these blessed teachings!* 🤲
        """
    
    await update.message.reply_text(hadith_text)

async def allah_names_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    page = int(context.args[0]) if context.args and context.args[0].isdigit() else 1
    await show_allah_names_page(update, page)

async def show_allah_names_page(update: Update, page: int, message_id=None):
    user_language = db.get_user_language(update.effective_user.id)
    names_per_page = 10
    start_idx = (page - 1) * names_per_page
    end_idx = start_idx + names_per_page
    
    names_list = ALLAH_NAMES_FULL[start_idx:end_idx]
    
    if user_language == 'ar':
        names_text = "🕋 *أسماء الله الحسنى*\n\n"
        footer = f"\n*الصفحة {page}/10 - عرض الأسماء {start_idx + 1}-{end_idx} من 99*"
        footer += "\n\n*من حفظها دخل الجنة.* (صحيح البخاري)"
    else:
        names_text = "🕋 *99 Names of Allah*\n\n"
        footer = f"\n*Page {page}/10 - Showing names {start_idx + 1}-{end_idx} of 99*"
        footer += "\n\n*Whoever memorizes them will enter Paradise.* (Sahih al-Bukhari)"
    
    for name in names_list:
        names_text += f"{name['number']}. *{name['arabic']}*\n"
        names_text += f"   {name['transliteration']} - {name['meaning']}\n\n"
    
    names_text += footer
    
    # Navigation with language support
    keyboard = []
    nav_buttons = []
    
    if page > 1:
        if user_language == 'ar':
            nav_buttons.append(InlineKeyboardButton("⬅️ السابق", callback_data=f"names_page_{page-1}"))
        else:
            nav_buttons.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"names_page_{page-1}"))
    
    total_pages = (len(ALLAH_NAMES_FULL) - 1) // names_per_page + 1
    nav_buttons.append(InlineKeyboardButton(f"{page}/{total_pages}", callback_data="noop"))
    
    if end_idx < len(ALLAH_NAMES_FULL):
        if user_language == 'ar':
            nav_buttons.append(InlineKeyboardButton("التالي ➡️", callback_data=f"names_page_{page+1}"))
        else:
            nav_buttons.append(InlineKeyboardButton("Next ➡️", callback_data=f"names_page_{page+1}"))
    
    if nav_buttons:
        keyboard.append(nav_buttons)
    
    if user_language == 'ar':
        keyboard.append([InlineKeyboardButton("↩️ العودة للرئيسية", callback_data="back_main")])
    else:
        keyboard.append([InlineKeyboardButton("↩️ Back to Main", callback_data="back_main")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if hasattr(update, 'callback_query') and update.callback_query:
        await update.callback_query.edit_message_text(names_text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(names_text, reply_markup=reply_markup)

async def duas_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_language = db.get_user_language(update.effective_user.id)
    
    if user_language == 'ar':
        duas_text = """
🤲 *الأدعية اليومية*

*دعاء الصباح:*
أَصْبَحْنَا وَأَصْبَحَ الْمُلْكُ لِلَّهِ، وَالْحَمْدُ لِلَّهِ، لَا إِلَٰهَ إِلَّا اللَّهُ وَحْدَهُ لَا شَرِيكَ لَهُ
"أصبحنا وأصبح الملك لله، والحمد لله، لا إله إلا الله وحده لا شريك له"

*دعاء المساء:*
أَمْسَيْنَا وَأَمْسَى الْمُلْكُ لِلَّهِ، وَالْحَمْدُ لِلَّهِ، لَا إِلَٰهَ إِلَّا اللَّهُ وَحْدَهُ لَا شَرِيكَ لَهُ
"أمسينا وأمسى الملك لله، والحمد لله، لا إله إلا الله وحده لا شريك له"

*دعاء طلب العلم:*
رَبِّ زِدْنِي عِلْمًا
"ربي زدني علماً" (سورة طه: 114)

*دعاء الحماية:*
أَعُوذُ بِكَلِمَاتِ اللَّهِ التَّامَّاتِ مِن شَرِّ مَا خَلَقَ
"أعوذ بكلمات الله التامات من شر ما خلق"

*دعاء المغفرة:*
رَبِّ اغْفِرْ لِي وَتُبْ عَلَيَّ إِنَّكَ أَنْتَ التَّوَّابُ الرَّحِيمُ
"ربي اغفر لي وتب علي إنك أنت التواب الرحيم"

*تقبل الله دعاءكم* 🤲
        """
    else:
        duas_text = """
🤲 *Daily Duas & Supplications*

*Morning Dua:*
أَصْبَحْنَا وَأَصْبَحَ الْمُلْكُ لِلَّهِ، وَالْحَمْدُ لِلَّهِ، لَا إِلَٰهَ إِلَّا اللَّهُ وَحْدَهُ لَا شَرِيكَ لَهُ
"We have reached the morning and at this very time all sovereignty belongs to Allah..."

*Evening Dua:*
أَمْسَيْنَا وَأَمْسَى الْمُلْكُ لِلَّهِ، وَالْحَمْدُ لِلَّهِ، لَا إِلَٰهَ إِلَّا اللَّهُ وَحْدَهُ لَا شَرِيكَ لَهُ
"We have reached the evening and at this very time all sovereignty belongs to Allah..."

*Dua for Knowledge:*
رَبِّ زِدْنِي عِلْمًا
"My Lord, increase me in knowledge." (Quran 20:114)

*Dua for Protection:*
أَعُوذُ بِكَلِمَاتِ اللَّهِ التَّامَّاتِ مِن شَرِّ مَا خَلَقَ
"I seek refuge in the perfect words of Allah from the evil of what He has created."

*Dua for Forgiveness:*
رَبِّ اغْفِرْ لِي وَتُبْ عَلَيَّ إِنَّكَ أَنْتَ التَّوَّابُ الرَّحِيمُ
"My Lord, forgive me and accept my repentance, for You are the Acceptor of Repentance, the Merciful."

*May Allah accept our supplications!* 🤲
        """
    
    await update.message.reply_text(duas_text)

async def hadith_categories_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_language = db.get_user_language(update.effective_user.id)
    
    if user_language == 'ar':
        keyboard = [
            [InlineKeyboardButton("📖 الإيمان والعقيدة", callback_data="hadith_faith")],
            [InlineKeyboardButton("❤️ الأخلاق والآداب", callback_data="hadith_manners")],
            [InlineKeyboardButton("👨‍👩‍👧‍👦 العلاقات الاجتماعية", callback_data="hadith_social")],
            [InlineKeyboardButton("🕌 العبادة والصلاة", callback_data="hadith_worship")],
            [InlineKeyboardButton("🎲 حديث عشوائي", callback_data="hadith_random")]
        ]
        text = "📚 *أقسام الأحاديث*\n\nاختر القسم لاستكشاف الأحاديث:"
    else:
        keyboard = [
            [InlineKeyboardButton("📖 Faith & Belief", callback_data="hadith_faith")],
            [InlineKeyboardButton("❤️ Manners & Character", callback_data="hadith_manners")],
            [InlineKeyboardButton("👨‍👩‍👧‍👦 Social Relations", callback_data="hadith_social")],
            [InlineKeyboardButton("🕌 Worship & Prayer", callback_data="hadith_worship")],
            [InlineKeyboardButton("🎲 Random Hadith", callback_data="hadith_random")]
        ]
        text = "📚 *Hadith Categories*\n\nSelect a category to explore Hadith:"
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(text, reply_markup=reply_markup)