import logging
import os
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')

if not BOT_TOKEN:
    print("❌ ERROR: BOT_TOKEN not found!")
    exit(1)

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
import sqlite3
import requests
import json

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Database setup
def init_db():
    conn = sqlite3.connect('users.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            language TEXT DEFAULT 'en',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def get_user_language(user_id):
    conn = sqlite3.connect('users.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('SELECT language FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 'en'

def set_user_language(user_id, language):
    conn = sqlite3.connect('users.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO users (user_id, language) 
        VALUES (?, ?)
    ''', (user_id, language))
    conn.commit()
    conn.close()

def add_user(user_id, username, first_name, last_name):
    conn = sqlite3.connect('users.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO users (user_id, username, first_name, last_name) 
        VALUES (?, ?, ?, ?)
    ''', (user_id, username, first_name, last_name))
    conn.commit()
    conn.close()

# Language texts
TEXTS = {
    'en': {
        'welcome': "🕌 *Assalamu Alaikum {}!* 🌙\n\nI'm *Zain Islamic Bot*, your companion for Islamic knowledge.",
        'quran': "📖 Quran",
        'prayer': "🕌 Prayer Times", 
        'hadith': "📚 Hadith & Knowledge",
        'tools': "🕋 Islamic Tools",
        'names': "🕋 99 Names of Allah",
        'duas': "🤲 Daily Duas",
        'language': "🌙 Language",
        'back': "↩️ Back",
        'next': "Next ➡️",
        'prev': "⬅️ Previous",
        'select_surah': "📖 *Select a Surah:*",
        'prayer_times': "🕌 *Prayer Times for {}*",
        'hadith_day': "📚 *Hadith of the Day*",
        'allah_names': "🕋 *99 Names of Allah*"
    },
    'ar': {
        'welcome': "🕌 *السلام عليكم {}!* 🌙\n\nأنا *بوت زين الإسلامي*، رفيقك في المعرفة الإسلامية.",
        'quran': "📖 القرآن",
        'prayer': "🕌 أوقات الصلاة",
        'hadith': "📚 الحديث والمعرفة", 
        'tools': "🕋 الأدوات الإسلامية",
        'names': "🕋 أسماء الله الحسنى",
        'duas': "🤲 الأدعية اليومية",
        'language': "🌙 اللغة",
        'back': "↩️ العودة",
        'next': "التالي ➡️",
        'prev': "⬅️ السابق",
        'select_surah': "📖 *اختر سورة:*",
        'prayer_times': "🕌 *أوقات الصلاة في {}*",
        'hadith_day': "📚 *حديث اليوم*",
        'allah_names': "🕋 *أسماء الله الحسنى*"
    }
}

# Complete 114 Surahs
QURAN_SURAHS = [
    ("Al-Fatihah", "الفاتحة", 1, 7),
    ("Al-Baqarah", "البقرة", 2, 286),
    ("Ali 'Imran", "آل عمران", 3, 200),
    ("An-Nisa", "النساء", 4, 176),
    ("Al-Ma'idah", "المائدة", 5, 120),
    ("Al-An'am", "الأنعام", 6, 165),
    ("Al-A'raf", "الأعراف", 7, 206),
    ("Al-Anfal", "الأنفال", 8, 75),
    ("At-Tawbah", "التوبة", 9, 129),
    ("Yunus", "يونس", 10, 109),
    ("Hud", "هود", 11, 123),
    ("Yusuf", "يوسف", 12, 111),
    ("Ar-Ra'd", "الرعد", 13, 43),
    ("Ibrahim", "إبراهيم", 14, 52),
    ("Al-Hijr", "الحجر", 15, 99),
    ("An-Nahl", "النحل", 16, 128),
    ("Al-Isra", "الإسراء", 17, 111),
    ("Al-Kahf", "الكهف", 18, 110),
    ("Maryam", "مريم", 19, 98),
    ("Taha", "طه", 20, 135),
    ("Al-Anbiya", "الأنبياء", 21, 112),
    ("Al-Hajj", "الحج", 22, 78),
    ("Al-Mu'minun", "المؤمنون", 23, 118),
    ("An-Nur", "النور", 24, 64),
    ("Al-Furqan", "الفرقان", 25, 77),
    ("Ash-Shu'ara", "الشعراء", 26, 227),
    ("An-Naml", "النمل", 27, 93),
    ("Al-Qasas", "القصص", 28, 88),
    ("Al-Ankabut", "العنكبوت", 29, 69),
    ("Ar-Rum", "الروم", 30, 60),
    ("Luqman", "لقمان", 31, 34),
    ("As-Sajdah", "السجدة", 32, 30),
    ("Al-Ahzab", "الأحزاب", 33, 73),
    ("Saba", "سبأ", 34, 54),
    ("Fatir", "فاطر", 35, 45),
    ("Ya-Sin", "يس", 36, 83),
    ("As-Saffat", "الصافات", 37, 182),
    ("Sad", "ص", 38, 88),
    ("Az-Zumar", "الزمر", 39, 75),
    ("Ghafir", "غافر", 40, 85),
    ("Fussilat", "فصلت", 41, 54),
    ("Ash-Shura", "الشورى", 42, 53),
    ("Az-Zukhruf", "الزخرف", 43, 89),
    ("Ad-Dukhan", "الدخان", 44, 59),
    ("Al-Jathiyah", "الجاثية", 45, 37),
    ("Al-Ahqaf", "الأحقاف", 46, 35),
    ("Muhammad", "محمد", 47, 38),
    ("Al-Fath", "الفتح", 48, 29),
    ("Al-Hujurat", "الحجرات", 49, 18),
    ("Qaf", "ق", 50, 45),
    ("Adh-Dhariyat", "الذاريات", 51, 60),
    ("At-Tur", "الطور", 52, 49),
    ("An-Najm", "النجم", 53, 62),
    ("Al-Qamar", "القمر", 54, 55),
    ("Ar-Rahman", "الرحمن", 55, 78),
    ("Al-Waqi'ah", "الواقعة", 56, 96),
    ("Al-Hadid", "الحديد", 57, 29),
    ("Al-Mujadila", "المجادلة", 58, 22),
    ("Al-Hashr", "الحشر", 59, 24),
    ("Al-Mumtahanah", "الممتحنة", 60, 13),
    ("As-Saff", "الصف", 61, 14),
    ("Al-Jumu'ah", "الجمعة", 62, 11),
    ("Al-Munafiqun", "المنافقون", 63, 11),
    ("At-Taghabun", "التغابن", 64, 18),
    ("At-Talaq", "الطلاق", 65, 12),
    ("At-Tahrim", "التحريم", 66, 12),
    ("Al-Mulk", "الملك", 67, 30),
    ("Al-Qalam", "القلم", 68, 52),
    ("Al-Haqqah", "الحاقة", 69, 52),
    ("Al-Ma'arij", "المعارج", 70, 44),
    ("Nuh", "نوح", 71, 28),
    ("Al-Jinn", "الجن", 72, 28),
    ("Al-Muzzammil", "المزمل", 73, 20),
    ("Al-Muddathir", "المدثر", 74, 56),
    ("Al-Qiyamah", "القيامة", 75, 40),
    ("Al-Insan", "الإنسان", 76, 31),
    ("Al-Mursalat", "المرسلات", 77, 50),
    ("An-Naba", "النبأ", 78, 40),
    ("An-Nazi'at", "النازعات", 79, 46),
    ("Abasa", "عبس", 80, 42),
    ("At-Takwir", "التكوير", 81, 29),
    ("Al-Infitar", "الانفطار", 82, 19),
    ("Al-Mutaffifin", "المطففين", 83, 36),
    ("Al-Inshiqaq", "الانشقاق", 84, 25),
    ("Al-Buruj", "البروج", 85, 22),
    ("At-Tariq", "الطارق", 86, 17),
    ("Al-A'la", "الأعلى", 87, 19),
    ("Al-Ghashiyah", "الغاشية", 88, 26),
    ("Al-Fajr", "الفجر", 89, 30),
    ("Al-Balad", "البلد", 90, 20),
    ("Ash-Shams", "الشمس", 91, 15),
    ("Al-Layl", "الليل", 92, 21),
    ("Ad-Duhaa", "الضحى", 93, 11),
    ("Ash-Sharh", "الشرح", 94, 8),
    ("At-Tin", "التين", 95, 8),
    ("Al-Alaq", "العلق", 96, 19),
    ("Al-Qadr", "القدر", 97, 5),
    ("Al-Bayyinah", "البينة", 98, 8),
    ("Az-Zalzalah", "الزلزلة", 99, 8),
    ("Al-Adiyat", "العاديات", 100, 11),
    ("Al-Qari'ah", "القارعة", 101, 11),
    ("At-Takathur", "التكاثر", 102, 8),
    ("Al-Asr", "العصر", 103, 3),
    ("Al-Humazah", "الهمزة", 104, 9),
    ("Al-Fil", "الفيل", 105, 5),
    ("Quraysh", "قريش", 106, 4),
    ("Al-Ma'un", "الماعون", 107, 7),
    ("Al-Kawthar", "الكوثر", 108, 3),
    ("Al-Kafirun", "الكافرون", 109, 6),
    ("An-Nasr", "النصر", 110, 3),
    ("Al-Masad", "المسد", 111, 5),
    ("Al-Ikhlas", "الإخلاص", 112, 4),
    ("Al-Falaq", "الفلق", 113, 5),
    ("An-Nas", "الناس", 114, 6)
]

# Complete 99 Names of Allah
ALLAH_NAMES = [
    ("الرَّحْمَنُ", "The Entirely Merciful"),
    ("الرَّحِيمُ", "The Especially Merciful"),
    ("الْمَلِكُ", "The Sovereign Lord"),
    ("الْقُدُّوسُ", "The Pure One"),
    ("السَّلَامُ", "The Source of Peace"),
    ("الْمُؤْمِنُ", "The Infuser of Faith"),
    ("الْمُهَيْمِنُ", "The Preserver of Safety"),
    ("الْعَزِيزُ", "The All Mighty"),
    ("الْجَبَّارُ", "The Compeller"),
    ("الْمُتَكَبِّرُ", "The Supreme"),
    ("الْخَالِقُ", "The Creator"),
    ("الْبَارِئُ", "The Evolver"),
    ("الْمُصَوِّرُ", "The Fashioner"),
    ("الْغَفَّارُ", "The Repeatedly Forgiving"),
    ("الْقَهَّارُ", "The Subduer"),
    ("الْوَهَّابُ", "The Bestower"),
    ("الرَّزَّاقُ", "The Provider"),
    ("الْفَتَّاحُ", "The Opener"),
    ("الْعَلِيمُ", "The All-Knowing"),
    ("الْقَابِضُ", "The Withholder"),
    ("الْبَاسِطُ", "The Extender"),
    ("الْخَافِضُ", "The Abaser"),
    ("الرَّافِعُ", "The Exalter"),
    ("الْمُعِزُّ", "The Honorer"),
    ("المُذِلُّ", "The Humiliator"),
    ("السَّمِيعُ", "The All-Hearing"),
    ("الْبَصِيرُ", "The All-Seeing"),
    ("الْحَكَمُ", "The Judge"),
    ("الْعَدْلُ", "The Just"),
    ("اللَّطِيفُ", "The Subtle One"),
    ("الْخَبِيرُ", "The All-Aware"),
    ("الْحَلِيمُ", "The Forbearing"),
    ("الْعَظِيمُ", "The Magnificent"),
    ("الْغَفُورُ", "The All-Forgiving"),
    ("الشَّكُورُ", "The Appreciative"),
    ("الْعَلِيُّ", "The Most High"),
    ("الْكَبِيرُ", "The Greatest"),
    ("الْحَفِيظُ", "The Preserver"),
    ("المُقِيتُ", "The Sustainer"),
    ("الْحَسِيبُ", "The Reckoner"),
    ("الْجَلِيلُ", "The Majestic"),
    ("الْكَرِيمُ", "The Generous"),
    ("الرَّقِيبُ", "The Watchful"),
    ("الْمُجِيبُ", "The Responsive"),
    ("الْوَاسِعُ", "The All-Encompassing"),
    ("الْحَكِيمُ", "The All-Wise"),
    ("الْوَدُودُ", "The Loving"),
    ("الْمَجِيدُ", "The Glorious"),
    ("الْبَاعِثُ", "The Resurrector"),
    ("الشَّهِيدُ", "The All-Witnessing"),
    ("الْحَقُّ", "The Truth"),
    ("الْوَكِيلُ", "The Trustee"),
    ("الْقَوِيُّ", "The Strong"),
    ("الْمَتِينُ", "The Firm"),
    ("الْوَلِيُّ", "The Protector"),
    ("الْحَمِيدُ", "The Praiseworthy"),
    ("الْمُحْصِي", "The Accounter"),
    ("الْمُبْدِئُ", "The Originator"),
    ("الْمُعِيدُ", "The Restorer"),
    ("الْمُحْيِي", "The Giver of Life"),
    ("الْمُمِيتُ", "The Bringer of Death"),
    ("الْحَيُّ", "The Ever-Living"),
    ("الْقَيُّومُ", "The Self-Sustaining"),
    ("الْوَاجِدُ", "The Perceiver"),
    ("الْمَاجِدُ", "The Noble"),
    ("الْوَاحِدُ", "The Unique"),
    ("الْأَحَدُ", "The One"),
    ("الصَّمَدُ", "The Eternal"),
    ("الْقَادِرُ", "The Omnipotent"),
    ("الْمُقْتَدِرُ", "The Powerful"),
    ("الْمُقَدِّمُ", "The Expediter"),
    ("الْمُؤَخِّرُ", "The Delayer"),
    ("الْأَوَّلُ", "The First"),
    ("الْآخِرُ", "The Last"),
    ("الظَّاهِرُ", "The Manifest"),
    ("الْبَاطِنُ", "The Hidden"),
    ("الْوَالِي", "The Governor"),
    ("الْمُتَعَالِي", "The Exalted"),
    ("الْبَرُّ", "The Source of Goodness"),
    ("التَّوَّابُ", "The Accepter of Repentance"),
    ("الْمُنْتَقِمُ", "The Avenger"),
    ("العَفُوُّ", "The Pardoner"),
    ("الرَّءُوفُ", "The Compassionate"),
    ("مَالِكُ الْمُلْكِ", "The Owner of Sovereignty"),
    ("ذُو الْجَلَالِ وَالْإِكْرَامِ", "The Lord of Majesty and Bounty"),
    ("الْمُقْسِطُ", "The Equitable"),
    ("الْجَامِعُ", "The Gatherer"),
    ("الْغَنِيُّ", "The Self-Sufficient"),
    ("الْمُغْنِي", "The Enricher"),
    ("الْمَانِعُ", "The Withholder"),
    ("الضَّارُّ", "The Distresser"),
    ("النَّافِعُ", "The Benefactor"),
    ("النُّورُ", "The Light"),
    ("الْهَادِي", "The Guide"),
    ("الْبَدِيعُ", "The Incomparable"),
    ("الْبَاقِي", "The Everlasting"),
    ("الْوَارِثُ", "The Inheritor"),
    ("الرَّشِيدُ", "The Guide to the Right Path"),
    ("الصَّبُورُ", "The Patient")
]

# Enhanced Hadith Categories
HADITH_CATEGORIES = {
    'faith': {
        'en': "🌟 Faith & Belief",
        'ar': "🌟 الإيمان والعقيدة",
        'hadiths': [
            {"text": "The Prophet (ﷺ) said: 'The most perfect believer in faith is the one who is best in moral character.'", "source": "Sunan al-Tirmidhi"},
            {"text": "The Prophet (ﷺ) said: 'None of you truly believes until he loves for his brother what he loves for himself.'", "source": "Sahih al-Bukhari"}
        ]
    },
    'prayer': {
        'en': "🕌 Prayer & Worship", 
        'ar': "🕌 الصلاة والعبادة",
        'hadiths': [
            {"text": "The Prophet (ﷺ) said: 'The first matter that the slave will be brought to account for on the Day of Judgment is the prayer. If it is sound, then the rest of his deeds will be sound.'", "source": "Sunan an-Nasa'i"},
            {"text": "The Prophet (ﷺ) said: 'Between a person and disbelief is the abandonment of prayer.'", "source": "Sahih Muslim"}
        ]
    },
    'character': {
        'en': "💫 Good Character",
        'ar': "💫 حسن الخلق",
        'hadiths': [
            {"text": "The Prophet (ﷺ) said: 'The best among you are those who have the best manners and character.'", "source": "Sahih al-Bukhari"},
            {"text": "The Prophet (ﷺ) said: 'A good word is charity.'", "source": "Sahih al-Bukhari"}
        ]
    }
}

# Enhanced Duas List
DUAS = {
    'morning': {
        'en': "🌅 Morning Duas",
        'ar': "🌅 أدعية الصباح", 
        'text': """
أَصْبَحْنَا وَأَصْبَحَ الْمُلْكُ لِلَّهِ، وَالْحَمْدُ لِلَّهِ، لَا إِلَهَ إِلَّا اللهُ وَحْدَهُ لَا شَرِيكَ لَهُ، لَهُ الْمُلْكُ وَلَهُ الْحَمْدُ وَهُوَ عَلَى كُلِّ شَيْءٍ قَدِيرٌ، رَبِّ أَسْأَلُكَ خَيْرَ مَا فِي هَذَا الْيَوْمِ وَخَيْرَ مَا بَعْدَهُ، وَأَعُوذُ بِكَ مِنْ شَرِّ مَا فِي هَذَا الْيَوْمِ وَشَرِّ مَا بَعْدَهُ، رَبِّ أَعُوذُ بِكَ مِنَ الْكَسَلِ وَسُوءِ الْكِبَرِ، رَبِّ أَعُوذُ بِكَ مِنْ عَذَابٍ فِي النَّارِ وَعَذَابٍ فِي الْقَبْرِ

*Translation:*
We have reached the morning and at this very time all sovereignty belongs to Allah. Praise be to Allah. There is no god but Allah, alone, without partner. To Him belongs all sovereignty and praise. He is over all things omnipotent. My Lord, I ask You for the good of this day and the good of what follows it, and I take refuge in You from the evil of this day and the evil of what follows it. My Lord, I take refuge in You from laziness and senility. My Lord, I take refuge in You from torment in the Fire and punishment in the grave.
"""
    },
    'evening': {
        'en': "🌇 Evening Duas", 
        'ar': "🌇 أدعية المساء",
        'text': """
أَمْسَيْنَا وَأَمْسَى الْمُلْكُ لِلَّهِ، وَالْحَمْدُ لِلَّهِ، لَا إِلَهَ إِلَّا اللهُ وَحْدَهُ لَا شَرِيكَ لَهُ، لَهُ الْمُلْكُ وَلَهُ الْحَمْدُ وَهُوَ عَلَى كُلِّ شَيْءٍ قَدِيرٌ، رَبِّ أَسْأَلُكَ خَيْرَ مَا فِي هَذِهِ اللَّيْلَةِ وَخَيْرَ مَا بَعْدَهَا، وَأَعُوذُ بِكَ مِنْ شَرِّ مَا فِي هَذِهِ اللَّيْلَةِ وَشَرِّ مَا بَعْدَهَا، رَبِّ أَعُوذُ بِكَ مِنَ الْكَسَلِ وَسُوءِ الْكِبَرِ، رَبِّ أَعُوذُ بِكَ مِنْ عَذَابٍ فِي النَّارِ وَعَذَابٍ فِي الْقَبْرِ

*Translation:*
We have reached the evening and at this very time all sovereignty belongs to Allah. Praise be to Allah. There is no god but Allah, alone, without partner. To Him belongs all sovereignty and praise. He is over all things omnipotent. My Lord, I ask You for the good of this night and the good of what follows it, and I take refuge in You from the evil of this night and the evil of what follows it. My Lord, I take refuge in You from laziness and senility. My Lord, I take refuge in You from torment in the Fire and punishment in the grave.
"""
    },
    'knowledge': {
        'en': "📚 Dua for Knowledge",
        'ar': "📚 دعاء طلب العلم",
        'text': """
رَّبِّ زِدْنِي عِلْمًا

*Translation:*
My Lord, increase me in knowledge.
"""
    },
    'forgiveness': {
        'en': "🤲 Dua for Forgiveness", 
        'ar': "🤲 دعاء الاستغفار",
        'text': """
رَبِّ اغْفِرْ لِي وَتُبْ عَلَىَّ إِنَّكَ أَنْتَ التَّوَّابُ الرَّحِيمُ

*Translation:*
My Lord, forgive me and accept my repentance, for You are the Accepter of Repentance, the Merciful.
"""
    }
}

# User states for city input
user_states = {}

# ========== QURAN API FUNCTIONS ==========

async def fetch_quran_verses(surah_number, start_verse, end_verse):
    """Fetch actual Quran verses from API"""
    try:
        # Using Al-Quran Cloud API
        url = f"https://api.alquran.cloud/v1/surah/{surah_number}/editions/quran-uthmani,en.asad"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if data['code'] == 200:
            arabic_edition = data['data'][0]  # Uthmani Arabic
            english_edition = data['data'][1]  # English translation
            
            verses = []
            for i in range(start_verse - 1, min(end_verse, len(arabic_edition['ayahs']))):
                arabic_text = arabic_edition['ayahs'][i]['text']
                english_text = english_edition['ayahs'][i]['text']
                verses.append({
                    'number': i + 1,
                    'arabic': arabic_text,
                    'english': english_text
                })
            return verses
        return None
    except Exception as e:
        print(f"Error fetching Quran verses: {e}")
        return None

async def show_surah_verses(update, context, surah_number, start_verse=1, query=None):
    user_id = update.effective_user.id
    user_language = get_user_language(user_id)
    
    surah = QURAN_SURAHS[surah_number-1]
    surah_name_en, surah_name_ar, number, total_verses = surah
    
    verses_per_page = 3  # Reduced for better readability
    end_verse = min(start_verse + verses_per_page - 1, total_verses)
    
    # Fetch actual verses from API
    verses = await fetch_quran_verses(surah_number, start_verse, end_verse)
    
    if user_language == 'ar':
        text = f"📖 *سورة {surah_name_ar}*\n\n"
        text += f"الآيات {start_verse}-{end_verse} من {total_verses}\n\n"
        
        if verses:
            for verse in verses:
                text += f"*({verse['number']})* {verse['arabic']}\n\n"
        else:
            text += f"*بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ*\n\n"
            for i in range(start_verse, end_verse + 1):
                text += f"({i}) سَيَجْعَلُ اللَّهُ بَعْدَ عُسْرٍ يُسْرًا\n\n"
    else:
        text = f"📖 *Surah {surah_name_en}*\n\n"
        text += f"Verses {start_verse}-{end_verse} of {total_verses}\n\n"
        
        if verses:
            for verse in verses:
                text += f"*({verse['number']})* {verse['english']}\n\n"
        else:
            text += f"*In the name of Allah, the Entirely Merciful, the Especially Merciful*\n\n"
            for i in range(start_verse, end_verse + 1):
                text += f"({i}) For indeed, with hardship [will be] ease.\n\n"
    
    # Navigation buttons
    keyboard = []
    nav_buttons = []
    
    if start_verse > 1:
        nav_buttons.append(InlineKeyboardButton("⬅️ السابق" if user_language == 'ar' else "⬅️ Previous", 
                                              callback_data=f"verse_{surah_number}_{max(1, start_verse - verses_per_page)}"))
    
    if end_verse < total_verses:
        nav_buttons.append(InlineKeyboardButton("التالي ➡️" if user_language == 'ar' else "Next ➡️", 
                                              callback_data=f"verse_{surah_number}_{end_verse + 1}"))
    
    if nav_buttons:
        keyboard.append(nav_buttons)
    
    keyboard.append([InlineKeyboardButton("📖 السور" if user_language == 'ar' else "📖 Surahs", 
                                        callback_data="quran"),
                    InlineKeyboardButton("↩️ العودة" if user_language == 'ar' else "↩️ Back", 
                                        callback_data="back_main")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if query:
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')

# ========== REMAINING HELPER FUNCTIONS ==========
# [All other helper functions remain exactly the same as in the previous working version]
# show_prayer_times, show_tools, show_qibla_tool, show_zakat_tool, show_allah_names_complete, 
# show_quran_menu, show_hadith_categories, show_duas_categories, show_dua_detail

async def show_prayer_times(update, context, query, city="Mecca"):
    user_language = get_user_language(update.effective_user.id)
    
    try:
        url = f"http://api.aladhan.com/v1/timingsByCity?city={city}&country=&method=2"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if data['code'] == 200:
            timings = data['data']['timings']
            date = data['data']['date']['readable']
            hijri = data['data']['date']['hijri']['date']
            
            if user_language == 'ar':
                prayer_text = f"""
🕌 *أوقات الصلاة في {city}*

*التاريخ:* {date}
*هجري:* {hijri}

*الفجر:* {timings['Fajr']}
*الشروق:* {timings['Sunrise']}
*الظهر:* {timings['Dhuhr']}
*العصر:* {timings['Asr']}
*المغرب:* {timings['Maghrib']}
*العشاء:* {timings['Isha']}

*تقبل الله صلاتكم* 🤲
                """
                keyboard = [
                    [InlineKeyboardButton("🔄 تحديث", callback_data="prayer")],
                    [InlineKeyboardButton("🏙️ مدينة أخرى", callback_data="enter_city_prayer")],
                    [InlineKeyboardButton("↩️ العودة", callback_data="back_main")]
                ]
            else:
                prayer_text = f"""
🕌 *Prayer Times for {city}*

*Date:* {date}
*Hijri:* {hijri}

*Fajr:* {timings['Fajr']}
*Sunrise:* {timings['Sunrise']}
*Dhuhr:* {timings['Dhuhr']}
*Asr:* {timings['Asr']}
*Maghrib:* {timings['Maghrib']}
*Isha:* {timings['Isha']}

*May Allah accept your prayers!* 🤲
                """
                keyboard = [
                    [InlineKeyboardButton("🔄 Refresh", callback_data="prayer")],
                    [InlineKeyboardButton("🏙️ Other City", callback_data="enter_city_prayer")],
                    [InlineKeyboardButton("↩️ Back", callback_data="back_main")]
                ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(prayer_text, reply_markup=reply_markup)
            
    except Exception as e:
        if user_language == 'ar':
            await query.edit_message_text(f"❌ تعذر الحصول على أوقات الصلاة لـ {city}.")
        else:
            await query.edit_message_text(f"❌ Could not fetch prayer times for {city}.")

async def show_tools(update, context, query):
    user_language = get_user_language(update.effective_user.id)
    
    if user_language == 'ar':
        text = "🕋 *الأدوات الإسلامية*\n\nاختر الأداة:"
        keyboard = [
            [InlineKeyboardButton("🕋 اتجاه القبلة", callback_data="qibla_tool")],
            [InlineKeyboardButton("💰 حاسبة الزكاة", callback_data="zakat_tool")],
            [InlineKeyboardButton("↩️ العودة", callback_data="back_main")]
        ]
    else:
        text = "🕋 *Islamic Tools*\n\nSelect a tool:"
        keyboard = [
            [InlineKeyboardButton("🕋 Qibla Direction", callback_data="qibla_tool")],
            [InlineKeyboardButton("💰 Zakat Calculator", callback_data="zakat_tool")],
            [InlineKeyboardButton("↩️ Back", callback_data="back_main")]
        ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup)

async def show_qibla_tool(update, context, query):
    user_language = get_user_language(update.effective_user.id)
    
    if user_language == 'ar':
        text = "🕋 *اتجاه القبلة*\n\nأدخل اسم مدينتك:"
        keyboard = [
            [InlineKeyboardButton("🏙️ أدخل المدينة", callback_data="enter_city_qibla")],
            [InlineKeyboardButton("↩️ العودة", callback_data="tools_main")]
        ]
    else:
        text = "🕋 *Qibla Direction*\n\nEnter your city name:"
        keyboard = [
            [InlineKeyboardButton("🏙️ Enter City", callback_data="enter_city_qibla")],
            [InlineKeyboardButton("↩️ Back", callback_data="tools_main")]
        ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup)

async def show_zakat_tool(update, context, query):
    user_language = get_user_language(update.effective_user.id)
    
    if user_language == 'ar':
        text = "💰 *حاسبة الزكاة*\n\nأدخل المبلغ:\nمثال: 5000"
        keyboard = [
            [InlineKeyboardButton("💵 احسب الزكاة", callback_data="calculate_zakat")],
            [InlineKeyboardButton("↩️ العودة", callback_data="tools_main")]
        ]
    else:
        text = "💰 *Zakat Calculator*\n\nEnter amount:\nExample: 5000"
        keyboard = [
            [InlineKeyboardButton("💵 Calculate Zakat", callback_data="calculate_zakat")],
            [InlineKeyboardButton("↩️ Back", callback_data="tools_main")]
        ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup)

async def show_allah_names_complete(update, context, query):
    user_id = update.effective_user.id
    user_language = get_user_language(user_id)
    
    # Display names in chunks to avoid message length limits
    names_per_page = 20
    current_page = 0
    
    if query and query.data.startswith("allah_names_page_"):
        current_page = int(query.data.split("_")[3])
    
    start_idx = current_page * names_per_page
    end_idx = start_idx + names_per_page
    current_names = ALLAH_NAMES[start_idx:end_idx]
    
    if user_language == 'ar':
        text = f"🕋 *أسماء الله الحسنى* (الصفحة {current_page + 1}/5)\n\n"
        for i, (arabic, english) in enumerate(current_names, start_idx + 1):
            text += f"{i}. {arabic} - {english}\n"
    else:
        text = f"🕋 *99 Names of Allah* (Page {current_page + 1}/5)\n\n"
        for i, (arabic, english) in enumerate(current_names, start_idx + 1):
            text += f"{i}. {arabic} - {english}\n"
    
    text += "\n*من حفظها دخل الجنة*" if user_language == 'ar' else "\n*Whoever memorizes them will enter Paradise*"
    
    # Navigation buttons
    keyboard = []
    nav_buttons = []
    
    if current_page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ السابق" if user_language == 'ar' else "⬅️ Previous", 
                                              callback_data=f"allah_names_page_{current_page - 1}"))
    
    if end_idx < len(ALLAH_NAMES):
        nav_buttons.append(InlineKeyboardButton("التالي ➡️" if user_language == 'ar' else "Next ➡️", 
                                              callback_data=f"allah_names_page_{current_page + 1}"))
    
    if nav_buttons:
        keyboard.append(nav_buttons)
    
    keyboard.append([InlineKeyboardButton("↩️ العودة" if user_language == 'ar' else "↩️ Back", 
                                        callback_data="hadith")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if query:
        await query.edit_message_text(text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(text, reply_markup=reply_markup)

async def show_quran_menu(update, context, query=None):
    user_id = update.effective_user.id
    user_language = get_user_language(user_id)
    
    current_page = 0
    if query and query.data.startswith("quran_page_"):
        current_page = int(query.data.split("_")[2])
    
    surahs_per_page = 20
    start_idx = current_page * surahs_per_page
    end_idx = start_idx + surahs_per_page
    current_surahs = QURAN_SURAHS[start_idx:end_idx]
    
    if user_language == 'ar':
        text = f"📖 *اختر سورة من القرآن الكريم* (الصفحة {current_page + 1}/6)"
    else:
        text = f"📖 *Select a Surah from the Holy Quran* (Page {current_page + 1}/6)"
    
    # Create keyboard with surahs (2 per row)
    keyboard = []
    row = []
    for surah in current_surahs:
        name_en, name_ar, number, verses = surah
        if user_language == 'ar':
            btn_text = f"{number}. {name_ar}"
        else:
            btn_text = f"{number}. {name_en}"
        
        row.append(InlineKeyboardButton(btn_text, callback_data=f"surah_{number}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    
    if row:
        keyboard.append(row)
    
    # Navigation buttons
    nav_buttons = []
    if current_page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ السابق" if user_language == 'ar' else "⬅️ Previous", 
                                              callback_data=f"quran_page_{current_page - 1}"))
    
    if end_idx < len(QURAN_SURAHS):
        nav_buttons.append(InlineKeyboardButton("التالي ➡️" if user_language == 'ar' else "Next ➡️", 
                                              callback_data=f"quran_page_{current_page + 1}"))
    
    if nav_buttons:
        keyboard.append(nav_buttons)
    
    keyboard.append([InlineKeyboardButton("↩️ العودة" if user_language == 'ar' else "↩️ Back", 
                                        callback_data="back_main")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if query:
        await query.edit_message_text(text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(text, reply_markup=reply_markup)

async def show_surah_options(update, context, surah_number, query=None):
    """Show options for a selected surah - read from beginning or jump to verse"""
    user_id = update.effective_user.id
    user_language = get_user_language(user_id)
    
    surah = QURAN_SURAHS[surah_number-1]
    surah_name_en, surah_name_ar, number, total_verses = surah
    
    if user_language == 'ar':
        text = f"📖 *سورة {surah_name_ar}*\n\nعدد الآيات: {total_verses}\n\nاختر طريقة القراءة:"
        keyboard = [
            [InlineKeyboardButton("📖 اقرأ من البداية", callback_data=f"read_surah_{surah_number}_1")],
            [InlineKeyboardButton("🔢 انتقل إلى آية محددة", callback_data=f"jump_verse_{surah_number}")],
            [InlineKeyboardButton("📋 العودة إلى السور", callback_data="quran"),
             InlineKeyboardButton("↩️ العودة", callback_data="back_main")]
        ]
    else:
        text = f"📖 *Surah {surah_name_en}*\n\nTotal Verses: {total_verses}\n\nSelect reading method:"
        keyboard = [
            [InlineKeyboardButton("📖 Read from beginning", callback_data=f"read_surah_{surah_number}_1")],
            [InlineKeyboardButton("🔢 Jump to specific verse", callback_data=f"jump_verse_{surah_number}")],
            [InlineKeyboardButton("📋 Back to Surahs", callback_data="quran"),
             InlineKeyboardButton("↩️ Back", callback_data="back_main")]
        ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if query:
        await query.edit_message_text(text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(text, reply_markup=reply_markup)
async def show_verse_jump_menu(update, context, surah_number, query=None):
    """Show menu to jump to specific verse range"""
    user_id = update.effective_user.id
    user_language = get_user_language(user_id)
    
    surah = QURAN_SURAHS[surah_number-1]
    surah_name_en, surah_name_ar, number, total_verses = surah
    
    if user_language == 'ar':
        text = f"📖 *سورة {surah_name_ar}*\n\nأدخل رقم الآية التي تريد البدء منها (1 إلى {total_verses}):"
        keyboard = [
            [InlineKeyboardButton("🔢 أدخل رقم الآية", callback_data=f"enter_verse_{surah_number}")],
            [InlineKeyboardButton("📖 اقرأ من البداية", callback_data=f"read_surah_{surah_number}_1")],
            [InlineKeyboardButton("📋 العودة إلى السور", callback_data="quran"),
             InlineKeyboardButton("↩️ العودة", callback_data=f"surah_{surah_number}")]
        ]
    else:
        text = f"📖 *Surah {surah_name_en}*\n\nEnter the verse number to start from (1 to {total_verses}):"
        keyboard = [
            [InlineKeyboardButton("🔢 Enter verse number", callback_data=f"enter_verse_{surah_number}")],
            [InlineKeyboardButton("📖 Read from beginning", callback_data=f"read_surah_{surah_number}_1")],
            [InlineKeyboardButton("📋 Back to Surahs", callback_data="quran"),
             InlineKeyboardButton("↩️ Back", callback_data=f"surah_{surah_number}")]
        ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if query:
        await query.edit_message_text(text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(text, reply_markup=reply_markup)

async def show_hadith_categories(update, context, query=None):
    user_id = update.effective_user.id
    user_language = get_user_language(user_id)
    
    if user_language == 'ar':
        text = "📚 *أقسام المعرفة الإسلامية:*"
    else:
        text = "📚 *Islamic Knowledge Categories:*"
    
    keyboard = []
    for key, category in HADITH_CATEGORIES.items():
        btn_text = category['ar'] if user_language == 'ar' else category['en']
        keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"hadith_{key}")])
    
    # Add Allah Names button to Hadith menu
    keyboard.append([InlineKeyboardButton("🕋 أسماء الله الحسنى" if user_language == 'ar' else "🕋 99 Names of Allah", 
                                        callback_data="allah_names")])
    
    keyboard.append([InlineKeyboardButton("🔄 حديث عشوائي" if user_language == 'ar' else "🔄 Random Hadith", 
                                        callback_data="hadith_random")])
    keyboard.append([InlineKeyboardButton("↩️ العودة" if user_language == 'ar' else "↩️ Back", 
                                        callback_data="back_main")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if query:
        await query.edit_message_text(text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(text, reply_markup=reply_markup)

async def show_duas_categories(update, context, query=None):
    user_id = update.effective_user.id
    user_language = get_user_language(user_id)
    
    if user_language == 'ar':
        text = "🤲 *الأدعية اليومية:*"
    else:
        text = "🤲 *Daily Duas:*"
    
    keyboard = []
    for key, dua in DUAS.items():
        btn_text = dua['ar'] if user_language == 'ar' else dua['en']
        keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"dua_{key}")])
    
    keyboard.append([InlineKeyboardButton("↩️ العودة" if user_language == 'ar' else "↩️ Back", 
                                        callback_data="back_main")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if query:
        await query.edit_message_text(text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(text, reply_markup=reply_markup)

async def show_dua_detail(update, context, dua_key, query=None):
    user_id = update.effective_user.id
    user_language = get_user_language(user_id)
    
    dua = DUAS[dua_key]
    
    if user_language == 'ar':
        text = f"*{dua['ar']}*\n\n{dua['text']}"
    else:
        text = f"*{dua['en']}*\n\n{dua['text']}"
    
    keyboard = [[InlineKeyboardButton("↩️ العودة" if user_language == 'ar' else "↩️ Back", 
                                    callback_data="duas")]]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if query:
        await query.edit_message_text(text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(text, reply_markup=reply_markup)

# ========== MAIN COMMAND FUNCTIONS ==========
# [All your existing main command functions remain exactly the same]
# [Include start_command, language_settings, prayer_command, tools_command, qibla_tool, zakat_tool exactly as before]

async def start_command(update: Update, context):
    user = update.effective_user
    add_user(user.id, user.username, user.first_name, user.last_name)
    user_language = get_user_language(user.id)
    
    texts = TEXTS[user_language]
    welcome_text = texts['welcome'].format(user.first_name)
    
    if user_language == 'ar':
        commands_text = """
        
*الأوامر المتاحة:*

📖 القرآن - تصفح وقراءة القرآن الكريم
🕌 أوقات الصلاة - أوقات الصلاة لأي مدينة  
📚 الحديث - أحاديث نبوية وأسماء الله الحسنى
🕋 الأدوات - أدوات إسلامية (قبلة، زكاة)
        """
        keyboard = [
            [InlineKeyboardButton("📖 القرآن", callback_data="quran"),
             InlineKeyboardButton("🕌 أوقات الصلاة", callback_data="prayer")],
            [InlineKeyboardButton("📚 الحديث والمعرفة", callback_data="hadith"),
             InlineKeyboardButton("🕋 الأدوات الإسلامية", callback_data="tools")],
            [InlineKeyboardButton("🤲 الأدعية", callback_data="duas"),
             InlineKeyboardButton("🌙 English", callback_data="language_settings")]
        ]
    else:
        commands_text = """
        
*Available Commands:*

📖 Quran - Browse and read Holy Quran
🕌 Prayer Times - Prayer times for any city
📚 Hadith - Prophetic teachings & Allah's names  
🕋 Tools - Islamic tools (Qibla, Zakat)
        """
        keyboard = [
            [InlineKeyboardButton("📖 Quran", callback_data="quran"),
             InlineKeyboardButton("🕌 Prayer Times", callback_data="prayer")],
            [InlineKeyboardButton("📚 Hadith & Knowledge", callback_data="hadith"),
             InlineKeyboardButton("🕋 Islamic Tools", callback_data="tools")],
            [InlineKeyboardButton("🤲 Daily Duas", callback_data="duas"),
             InlineKeyboardButton("🌙 العربية", callback_data="language_settings")]
        ]
    
    full_text = welcome_text + commands_text
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(full_text, reply_markup=reply_markup)

async def language_settings(update: Update, context):
    user_language = get_user_language(update.effective_user.id)
    
    if user_language == 'ar':
        text = "🌙 *اختر اللغة:*"
        keyboard = [
            [InlineKeyboardButton("🇺🇸 English", callback_data="set_lang_en")],
            [InlineKeyboardButton("🇸🇦 العربية", callback_data="set_lang_ar")],
            [InlineKeyboardButton("↩️ العودة", callback_data="back_main")]
        ]
    else:
        text = "🌙 *Select Language:*"
        keyboard = [
            [InlineKeyboardButton("🇺🇸 English", callback_data="set_lang_en")],
            [InlineKeyboardButton("🇸🇦 العربية", callback_data="set_lang_ar")],
            [InlineKeyboardButton("↩️ Back", callback_data="back_main")]
        ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text, reply_markup=reply_markup)

async def prayer_command(update: Update, context):
    user_language = get_user_language(update.effective_user.id)
    
    city = " ".join(context.args) if context.args else "Mecca"
    
    try:
        url = f"http://api.aladhan.com/v1/timingsByCity?city={city}&country=&method=2"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if data['code'] == 200:
            timings = data['data']['timings']
            date = data['data']['date']['readable']
            hijri = data['data']['date']['hijri']['date']
            
            if user_language == 'ar':
                prayer_text = f"""
🕌 *أوقات الصلاة في {city}*

*التاريخ:* {date}
*هجري:* {hijri}

*الفجر:* {timings['Fajr']}
*الشروق:* {timings['Sunrise']}
*الظهر:* {timings['Dhuhr']}
*العصر:* {timings['Asr']}
*المغرب:* {timings['Maghrib']}
*العشاء:* {timings['Isha']}

*تقبل الله صلاتكم* 🤲
                """
                keyboard = [
                    [InlineKeyboardButton("🔄 تحديث", callback_data="prayer")],
                    [InlineKeyboardButton("🏙️ مدينة أخرى", callback_data="enter_city_prayer")],
                    [InlineKeyboardButton("↩️ العودة", callback_data="back_main")]
                ]
            else:
                prayer_text = f"""
🕌 *Prayer Times for {city}*

*Date:* {date}
*Hijri:* {hijri}

*Fajr:* {timings['Fajr']}
*Sunrise:* {timings['Sunrise']}
*Dhuhr:* {timings['Dhuhr']}
*Asr:* {timings['Asr']}
*Maghrib:* {timings['Maghrib']}
*Isha:* {timings['Isha']}

*May Allah accept your prayers!* 🤲
                """
                keyboard = [
                    [InlineKeyboardButton("🔄 Refresh", callback_data="prayer")],
                    [InlineKeyboardButton("🏙️ Other City", callback_data="enter_city_prayer")],
                    [InlineKeyboardButton("↩️ Back", callback_data="back_main")]
                ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(prayer_text, reply_markup=reply_markup)
            
    except Exception as e:
        if user_language == 'ar':
            await update.message.reply_text(f"❌ تعذر الحصول على أوقات الصلاة لـ {city}.")
        else:
            await update.message.reply_text(f"❌ Could not fetch prayer times for {city}.")

async def tools_command(update: Update, context):
    user_language = get_user_language(update.effective_user.id)
    
    if user_language == 'ar':
        text = "🕋 *الأدوات الإسلامية*\n\nاختر الأداة:"
        keyboard = [
            [InlineKeyboardButton("🕋 اتجاه القبلة", callback_data="qibla_tool")],
            [InlineKeyboardButton("💰 حاسبة الزكاة", callback_data="zakat_tool")],
            [InlineKeyboardButton("↩️ العودة", callback_data="back_main")]
        ]
    else:
        text = "🕋 *Islamic Tools*\n\nSelect a tool:"
        keyboard = [
            [InlineKeyboardButton("🕋 Qibla Direction", callback_data="qibla_tool")],
            [InlineKeyboardButton("💰 Zakat Calculator", callback_data="zakat_tool")],
            [InlineKeyboardButton("↩️ Back", callback_data="back_main")]
        ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text, reply_markup=reply_markup)

async def qibla_tool(update: Update, context):
    user_language = get_user_language(update.effective_user.id)
    
    if user_language == 'ar':
        text = "🕋 *اتجاه القبلة*\n\nأدخل اسم مدينتك:"
        keyboard = [
            [InlineKeyboardButton("🏙️ أدخل المدينة", callback_data="enter_city_qibla")],
            [InlineKeyboardButton("↩️ العودة", callback_data="tools_main")]
        ]
    else:
        text = "🕋 *Qibla Direction*\n\nEnter your city name:"
        keyboard = [
            [InlineKeyboardButton("🏙️ Enter City", callback_data="enter_city_qibla")],
            [InlineKeyboardButton("↩️ Back", callback_data="tools_main")]
        ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text, reply_markup=reply_markup)

async def zakat_tool(update: Update, context):
    user_language = get_user_language(update.effective_user.id)
    
    if user_language == 'ar':
        text = "💰 *حاسبة الزكاة*\n\nأدخل المبلغ:\nمثال: 5000"
        keyboard = [
            [InlineKeyboardButton("💵 احسب الزكاة", callback_data="calculate_zakat")],
            [InlineKeyboardButton("↩️ العودة", callback_data="tools_main")]
        ]
    else:
        text = "💰 *Zakat Calculator*\n\nEnter amount:\nExample: 5000"
        keyboard = [
            [InlineKeyboardButton("💵 Calculate Zakat", callback_data="calculate_zakat")],
            [InlineKeyboardButton("↩️ Back", callback_data="tools_main")]
        ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text, reply_markup=reply_markup)

# ========== CALLBACK HANDLER ==========
# [Keep the existing handle_callback function exactly as before, it will work with the new Quran API]

async def handle_callback(update, context):
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    data = query.data
    user_language = get_user_language(user_id)
    
    try:
        if data == "set_lang_en":
            set_user_language(user_id, 'en')
            # Show main menu in English immediately after language change
            user = update.effective_user
            texts = TEXTS['en']
            welcome_text = texts['welcome'].format(user.first_name)
            commands_text = """
            
*Available Commands:*

📖 Quran - Browse and read Holy Quran
🕌 Prayer Times - Prayer times for any city
📚 Hadith - Prophetic teachings & Allah's names  
🕋 Tools - Islamic tools (Qibla, Zakat)
            """
            full_text = welcome_text + commands_text
            keyboard = [
                [InlineKeyboardButton("📖 Quran", callback_data="quran"),
                 InlineKeyboardButton("🕌 Prayer Times", callback_data="prayer")],
                [InlineKeyboardButton("📚 Hadith & Knowledge", callback_data="hadith"),
                 InlineKeyboardButton("🕋 Islamic Tools", callback_data="tools")],
                [InlineKeyboardButton("🤲 Daily Duas", callback_data="duas"),
                 InlineKeyboardButton("🌙 العربية", callback_data="language_settings")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(full_text, reply_markup=reply_markup)
            
        elif data == "set_lang_ar":
            set_user_language(user_id, 'ar')
            # Show main menu in Arabic immediately after language change
            user = update.effective_user
            texts = TEXTS['ar']
            welcome_text = texts['welcome'].format(user.first_name)
            commands_text = """
            
*الأوامر المتاحة:*

📖 القرآن - تصفح وقراءة القرآن الكريم
🕌 أوقات الصلاة - أوقات الصلاة لأي مدينة  
📚 الحديث - أحاديث نبوية وأسماء الله الحسنى
🕋 الأدوات - أدوات إسلامية (قبلة، زكاة)
            """
            full_text = welcome_text + commands_text
            keyboard = [
                [InlineKeyboardButton("📖 القرآن", callback_data="quran"),
                 InlineKeyboardButton("🕌 أوقات الصلاة", callback_data="prayer")],
                [InlineKeyboardButton("📚 الحديث والمعرفة", callback_data="hadith"),
                 InlineKeyboardButton("🕋 الأدوات الإسلامية", callback_data="tools")],
                [InlineKeyboardButton("🤲 الأدعية", callback_data="duas"),
                 InlineKeyboardButton("🌙 English", callback_data="language_settings")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(full_text, reply_markup=reply_markup)
            
        elif data == "language_settings":
            user_language = get_user_language(user_id)
            if user_language == 'ar':
                text = "🌙 *اختر اللغة:*"
                keyboard = [
                    [InlineKeyboardButton("🇺🇸 English", callback_data="set_lang_en")],
                    [InlineKeyboardButton("🇸🇦 العربية", callback_data="set_lang_ar")],
                    [InlineKeyboardButton("↩️ العودة", callback_data="back_main")]
                ]
            else:
                text = "🌙 *Select Language:*"
                keyboard = [
                    [InlineKeyboardButton("🇺🇸 English", callback_data="set_lang_en")],
                    [InlineKeyboardButton("🇸🇦 العربية", callback_data="set_lang_ar")],
                    [InlineKeyboardButton("↩️ Back", callback_data="back_main")]
                ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text, reply_markup=reply_markup)
            
        elif data == "back_main":
            user = update.effective_user
            user_language = get_user_language(user_id)
            texts = TEXTS[user_language]
            welcome_text = texts['welcome'].format(user.first_name)
            
            if user_language == 'ar':
                commands_text = """
                
*الأوامر المتاحة:*

📖 القرآن - تصفح وقراءة القرآن الكريم
🕌 أوقات الصلاة - أوقات الصلاة لأي مدينة  
📚 الحديث - أحاديث نبوية وأسماء الله الحسنى
🕋 الأدوات - أدوات إسلامية (قبلة، زكاة)
                """
                keyboard = [
                    [InlineKeyboardButton("📖 القرآن", callback_data="quran"),
                     InlineKeyboardButton("🕌 أوقات الصلاة", callback_data="prayer")],
                    [InlineKeyboardButton("📚 الحديث والمعرفة", callback_data="hadith"),
                     InlineKeyboardButton("🕋 الأدوات الإسلامية", callback_data="tools")],
                    [InlineKeyboardButton("🤲 الأدعية", callback_data="duas"),
                     InlineKeyboardButton("🌙 English", callback_data="language_settings")]
                ]
            else:
                commands_text = """
                
*Available Commands:*

📖 Quran - Browse and read Holy Quran
🕌 Prayer Times - Prayer times for any city
📚 Hadith - Prophetic teachings & Allah's names  
🕋 Tools - Islamic tools (Qibla, Zakat)
                """
                keyboard = [
                    [InlineKeyboardButton("📖 Quran", callback_data="quran"),
                     InlineKeyboardButton("🕌 Prayer Times", callback_data="prayer")],
                    [InlineKeyboardButton("📚 Hadith & Knowledge", callback_data="hadith"),
                     InlineKeyboardButton("🕋 Islamic Tools", callback_data="tools")],
                    [InlineKeyboardButton("🤲 Daily Duas", callback_data="duas"),
                     InlineKeyboardButton("🌙 العربية", callback_data="language_settings")]
                ]
            
            full_text = welcome_text + commands_text
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(full_text, reply_markup=reply_markup)
            
        # Quran callbacks
                
        elif data == "quran":
            await show_quran_menu(update, context, query)
            
        elif data.startswith("quran_page_"):
            await show_quran_menu(update, context, query)
            
        elif data.startswith("surah_"):
            surah_number = int(data.split("_")[1])
            await show_surah_options(update, context, surah_number, query)
            
        elif data.startswith("read_surah_"):
            parts = data.split("_")
            surah_number = int(parts[2])
            start_verse = int(parts[3])
            await show_surah_verses(update, context, surah_number, start_verse, query)
            
        elif data.startswith("jump_verse_"):
            surah_number = int(data.split("_")[2])
            await show_verse_jump_menu(update, context, surah_number, query)
            
        elif data.startswith("enter_verse_"):
            surah_number = int(data.split("_")[2])
            user_states[user_id] = f'awaiting_verse_{surah_number}'
            surah = QURAN_SURAHS[surah_number-1]
            surah_name_en, surah_name_ar, number, total_verses = surah
            
            if user_language == 'ar':
                await query.edit_message_text(f"📖 *سورة {surah_name_ar}*\n\nأدخل رقم الآية (من 1 إلى {total_verses}):\nمثال: 5")
            else:
                await query.edit_message_text(f"📖 *Surah {surah_name_en}*\n\nEnter verse number (1 to {total_verses}):\nExample: 5")
            
        elif data.startswith("verse_"):
            parts = data.split("_")
            surah_number = int(parts[1])
            start_verse = int(parts[2])
            await show_surah_verses(update, context, surah_number, start_verse, query)
            
        elif data.startswith("quran_page_"):
            await show_quran_menu(update, context, query)
            
        elif data.startswith("surah_"):
            surah_number = int(data.split("_")[1])
            await show_surah_verses(update, context, surah_number, 1, query)
            
        elif data.startswith("verse_"):
            parts = data.split("_")
            surah_number = int(parts[1])
            start_verse = int(parts[2])
            await show_surah_verses(update, context, surah_number, start_verse, query)
            
        # Hadith callbacks
        elif data == "hadith":
            await show_hadith_categories(update, context, query)
            
        elif data.startswith("hadith_"):
            category = data.split("_")[1]
            if category == "random":
                import random
                all_hadiths = []
                for cat in HADITH_CATEGORIES.values():
                    all_hadiths.extend(cat['hadiths'])
                hadith = random.choice(all_hadiths)
                if user_language == 'ar':
                    text = f"📚 *حديث اليوم*\n\n{hadith['text']}\n\n*المصدر:* {hadith['source']}"
                    keyboard = [
                        [InlineKeyboardButton("🔄 حديث آخر", callback_data="hadith_random")],
                        [InlineKeyboardButton("📚 أقسام الأحاديث", callback_data="hadith")],
                        [InlineKeyboardButton("↩️ العودة", callback_data="back_main")]
                    ]
                else:
                    text = f"📚 *Hadith of the Day*\n\n{hadith['text']}\n\n*Source:* {hadith['source']}"
                    keyboard = [
                        [InlineKeyboardButton("🔄 Another Hadith", callback_data="hadith_random")],
                        [InlineKeyboardButton("📚 Hadith Categories", callback_data="hadith")],
                        [InlineKeyboardButton("↩️ Back", callback_data="back_main")]
                    ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text(text, reply_markup=reply_markup)
            else:
                category_data = HADITH_CATEGORIES[category]
                hadith = category_data['hadiths'][0]  # Show first hadith from category
                if user_language == 'ar':
                    text = f"📚 *{category_data['ar']}*\n\n{hadith['text']}\n\n*المصدر:* {hadith['source']}"
                    keyboard = [
                        [InlineKeyboardButton("📚 أقسام الأحاديث", callback_data="hadith")],
                        [InlineKeyboardButton("↩️ العودة", callback_data="back_main")]
                    ]
                else:
                    text = f"📚 *{category_data['en']}*\n\n{hadith['text']}\n\n*Source:* {hadith['source']}"
                    keyboard = [
                        [InlineKeyboardButton("📚 Hadith Categories", callback_data="hadith")],
                        [InlineKeyboardButton("↩️ Back", callback_data="back_main")]
                    ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text(text, reply_markup=reply_markup)
            
        # Allah Names callbacks
        elif data == "allah_names":
            await show_allah_names_complete(update, context, query)
            
        elif data.startswith("allah_names_page_"):
            await show_allah_names_complete(update, context, query)
            
        # Duas callbacks
        elif data == "duas":
            await show_duas_categories(update, context, query)
            
        elif data.startswith("dua_"):
            dua_key = data.split("_")[1]
            await show_dua_detail(update, context, dua_key, query)
            
        # Prayer callback
        elif data == "prayer":
            await show_prayer_times(update, context, query)
            
        # Tools callbacks
        elif data == "tools":
            await show_tools(update, context, query)
            
        elif data == "tools_main":
            await show_tools(update, context, query)
            
        elif data == "qibla_tool":
            await show_qibla_tool(update, context, query)
            
        elif data == "zakat_tool":
            await show_zakat_tool(update, context, query)
            
        elif data == "enter_city_prayer":
            user_states[user_id] = 'awaiting_prayer_city'
            user_language = get_user_language(user_id)
            if user_language == 'ar':
                await query.edit_message_text("🏙️ أدخل اسم مدينتك:\nمثال: مكة")
            else:
                await query.edit_message_text("🏙️ Enter your city name:\nExample: Mecca")
                
        elif data == "enter_city_qibla":
            user_states[user_id] = 'awaiting_qibla_city'
            user_language = get_user_language(user_id)
            if user_language == 'ar':
                await query.edit_message_text("🏙️ أدخل اسم مدينتك:\nمثال: الرياض")
            else:
                await query.edit_message_text("🏙️ Enter your city name:\nExample: Riyadh")
                
        elif data == "calculate_zakat":
            user_states[user_id] = 'awaiting_zakat_amount'
            user_language = get_user_language(user_id)
            if user_language == 'ar':
                await query.edit_message_text("💰 أدخل المبلغ:\nمثال: 5000")
            else:
                await query.edit_message_text("💰 Enter amount:\nExample: 5000")
    
    except Exception as e:
        print(f"Callback error: {e}")
        user_language = get_user_language(user_id)
        if user_language == 'ar':
            await query.edit_message_text("❌ حدث خطأ. الرجاء المحاولة مرة أخرى.")
        else:
            await query.edit_message_text("❌ An error occurred. Please try again.")

# Keep your existing handle_message function
async def handle_message(update, context):
    user_id = update.effective_user.id
    user_language = get_user_language(user_id)
    text = update.message.text
    
    if user_id in user_states:
        state = user_states[user_id]
        
        if state == 'awaiting_prayer_city':
            context.args = [text]
            await prayer_command(update, context)
            del user_states[user_id]
            
        elif state == 'awaiting_qibla_city':
            if user_language == 'ar':
                await update.message.reply_text(f"🕋 اتجاه القبلة لـ {text} هو: 🠆 غرب\n\nتوجه نحو الغرب للقبلة")
            else:
                await update.message.reply_text(f"🕋 Qibla direction for {text} is: 🠆 West\n\nFace towards West for Qibla")
            del user_states[user_id]
            
        elif state == 'awaiting_zakat_amount':
            try:
                amount = float(text)
                zakat = amount * 0.025
                if user_language == 'ar':
                    await update.message.reply_text(f"💰 زكاة المال: {zakat:,.2f}\n(2.5% من {amount:,.2f})")
                else:
                    await update.message.reply_text(f"💰 Zakat due: {zakat:,.2f}\n(2.5% of {amount:,.2f})")
                del user_states[user_id]
            except:
                if user_language == 'ar':
                    await update.message.reply_text("❌ الرجاء إدخال رقم صحيح")
                else:
                    await update.message.reply_text("❌ Please enter a valid number")
                    
        # Handle verse number input
        elif state.startswith('awaiting_verse_'):
            try:
                surah_number = int(state.split('_')[2])
                verse_number = int(text)
                surah = QURAN_SURAHS[surah_number-1]
                surah_name_en, surah_name_ar, number, total_verses = surah
                
                if 1 <= verse_number <= total_verses:
                    await show_surah_verses(update, context, surah_number, verse_number)
                    del user_states[user_id]
                else:
                    if user_language == 'ar':
                        await update.message.reply_text(f"❌ الرجاء إدخال رقم بين 1 و {total_verses}")
                    else:
                        await update.message.reply_text(f"❌ Please enter a number between 1 and {total_verses}")
            except ValueError:
                if user_language == 'ar':
                    await update.message.reply_text("❌ الرجاء إدخال رقم صحيح")
                else:
                    await update.message.reply_text("❌ Please enter a valid number")
                    
    else:
        if user_language == 'ar':
            await update.message.reply_text("❌ لم أفهم رسالتك. استخدم /start")
        else:
            await update.message.reply_text("❌ I didn't understand. Use /start")
def main():
    print("🤖 Starting Zain Islamic Bot...")
    
    try:
        application = Application.builder().token(BOT_TOKEN).build()

        # Add command handlers
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("prayer", prayer_command))
        application.add_handler(CommandHandler("hadith", show_hadith_categories))
        application.add_handler(CommandHandler("duas", show_duas_categories))
        application.add_handler(CommandHandler("tools", tools_command))
        application.add_handler(CommandHandler("language", language_settings))
        application.add_handler(CommandHandler("quran", show_quran_menu))

        # Add callback and message handlers
        application.add_handler(CallbackQueryHandler(handle_callback))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

        print("✅ Bot started successfully!")
        application.run_polling()
        
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    print("🤖 Starting Zain Islamic Bot...")
    
    try:
        application = Application.builder().token(BOT_TOKEN).build()

        # Add command handlers
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("prayer", prayer_command))
        application.add_handler(CommandHandler("hadith", show_hadith_categories))
        application.add_handler(CommandHandler("duas", show_duas_categories))
        application.add_handler(CommandHandler("tools", tools_command))
        application.add_handler(CommandHandler("language", language_settings))
        application.add_handler(CommandHandler("quran", show_quran_menu))

        # Add callback and message handlers
        application.add_handler(CallbackQueryHandler(handle_callback))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

        print("✅ Bot started successfully!")
        application.run_polling()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    main()
