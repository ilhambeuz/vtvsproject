"""
🎬 VTVS Premium Bot v2.0
━━━━━━━━━━━━━━━━━━━━━━━━
• Video → Voice + MP3
• YouTube / Instagram → Video (sifat tanlash) + Voice + MP3
• Premium: kesish, shovqin yo'qotish, cheksiz foydalanish
• 3 til: UZ / RU / EN (birinchi startda tanlanadi)
• Referral tizim (+bonus kun)
• Admin panel: statistika, broadcast, premium boshqaruv
"""

import asyncio
import logging
import os
import re
import sqlite3
import subprocess
from datetime import datetime, timedelta

import yt_dlp
from telegram import (
    InlineKeyboardButton as IKB,
    InlineKeyboardMarkup as IKM,
    KeyboardButton as KB,
    ReplyKeyboardMarkup as RKM,
    ReplyKeyboardRemove,
    Update,
)
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# ╔══════════════════════════════════════════════════════════╗
#                       SOZLAMALAR
# ╚══════════════════════════════════════════════════════════╝
BOT_TOKEN        = "8229173995:AAHFf2nBH8XCgM51hgxbulQtTQ0EzFk4M_k"
BOT_USERNAME     = "abdulhamidbot"          # @ siz
ADMIN_IDS        = [5016497622]         # Admin Telegram ID lari
TEMP_DIR         = "temp"
DB_PATH          = "vtvs.db"
PREMIUM_DAYS     = 30
PREMIUM_PRICE    = "$3"
FREE_DAILY_LIMIT = 5
REFERRAL_BONUS   = 3                   # bonus kun
MAX_TG_SIZE_MB   = 49                  # Telegram limit

os.makedirs(TEMP_DIR, exist_ok=True)
logging.basicConfig(format="%(asctime)s | %(levelname)s | %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

YT_RE = re.compile(
    r'(https?://)?(www\.)?(youtube\.com|youtu\.be|instagram\.com|instagr\.am)/.+'
)

# ╔══════════════════════════════════════════════════════════╗
#                     TARJIMALAR
# ╚══════════════════════════════════════════════════════════╝
T = {
    'uz': {
        'choose_lang':     "🌐 Tilni tanlang:",
        'lang_set':        "✅ Til: O'zbek",
        'welcome':         "👋 Salom, *{name}*!\n\n🎬 Video yuboring yoki YouTube/Instagram havolasini yuboring.\n\n📊 Reja: *{plan}*\n📈 Bugungi foydalanish: *{used}/{limit}*",
        'free_plan':       "🆓 Bepul",
        'premium_plan':    "⭐ Premium",
        'limit_reached':   "❌ Kunlik limit tugadi (*{limit}* ta).\n\n⭐ Premium oling — cheksiz foydalaning!",
        'processing':      "⏳ Qayta ishlanmoqda...",
        'downloading':     "⬇️ Yuklanmoqda...",
        'choose_quality':  "🎬 Sifatni tanlang:\n_(Free: 360p yoki Audio)_",
        'choose_quality_p':"🎬 Sifatni tanlang:",
        'choose_action':   "✅ Video yuklandi!\n⏱ Davomiylik: *{dur}*\n\nNima qilishni xohlaysiz?",
        'full_extract':    "▶️ To'liq ovoz",
        'trim_audio':      "✂️ Kesib olish",
        'enter_start':     "📍 *Boshlanish vaqtini* kiriting:\n_Misol: `1:30` yoki `90`_\n\nDavomiylik: *{dur}*",
        'enter_end':       "📍 *Tugash vaqtini* kiriting:\n_Misol: `3:00` yoki `180`_\n\nBoshlanish: *{start}*",
        'invalid_time':    "❌ Format noto'g'ri. Misol: `1:30` yoki `90`",
        'time_too_big':    "❌ Video {dur}. Kichikroq qiymat kiriting.",
        'end_less':        "❌ Tugash vaqti boshlanishdan katta bo'lishi kerak.",
        'voice_cap':       "🎤 Videodagi ovoz",
        'voice_trim_cap':  "🎤 Kesilgan ovoz: {start} → {end}",
        'mp3_cap':         "🎵 MP3 fayl",
        'mp3_trim_cap':    "🎵 Kesilgan MP3: {start}–{end}",
        'send_screenshot': "📸 To'lov chekining *screenshotini* yuboring:",
        'screenshot_sent': "✅ Screenshot yuborildi!\n⏳ Admin tekshirmoqda...",
        'pay_granted':     "🎉 *Tabriklaymiz!*\n✅ To'lov tasdiqlandi!\n⭐ *{days} kunlik Premium* faollashtirildi!\n📅 *{until}* gacha\n\n✂️ Endi video yuboring!",
        'pay_rejected':    "❌ *To'lovingiz tasdiqlanmadi.*\nTo'g'ri ma'lumot bilan qaytadan urinib ko'ring.",
        'premium_info':    "⭐ *Premium — {price}/oy*\n\n✅ Cheksiz foydalanish\n✂️ Istalgan vaqtdan kesish\n🔇 Shovqin yo'qotish\n📥 YouTube/Instagram (1080p gacha)\n\n{pay_details}",
        'pay_details':     "💳 *To'lov:*\n🔵 Click: `+998901234567`\n🟢 Payme: `+998901234567`\n💳 Uzcard: `8600 0000 0000 0000`",
        'i_paid':          "✅ To'lov qildim",
        'get_premium':     "⭐ Premium olish",
        'my_status':       "📊 Statusim",
        'referral_btn':    "👥 Referal",
        'referral_info':   "👥 *Referal dasturi*\n\nHar bir do'st uchun *+{bonus} kun* bonus!\n\n🔗 Havolangiz:\n`{link}`\n\n✅ Taklif qilganlar: *{count}* ta\n🎁 Bonus kunlar: *{days}* kun",
        'ref_bonus':       "🎁 *{name}* havolangiz orqali qo'shildi!\n+{bonus} kun bonus qo'shildi!",
        'no_video':        "❌ Video topilmadi. Qaytadan yuboring.",
        'error':           "❌ Xatolik. Qaytadan urinib ko'ring.",
        'hint':            "🎬 Video yuboring yoki havola!\n/start /premium /referral /language",
        'status_text':     "📊 *Status:*\n\n👤 *{name}*\n🎯 Reja: *{plan}*\n📈 Bugun: *{used}/{limit}*\n📅 Premium: *{until}*\n👥 Taklif: *{refs}* ta",
        'prem_until':      "{date} gacha",
        'no_prem':         "Yo'q",
        'file_too_big':    "⚠️ Fayl hajmi katta ({size} MB). Telegram 50MB gacha qabul qiladi.",
        'noise_remove':    "🔇 Shovqin yo'qotish (Premium)",
        'noise_done':      "🔇 Shovqin yo'qotildi!",
        'q360': "📱 360p", 'q480': "💻 480p (Premium)", 'q720': "🖥 720p (Premium)", 'q1080': "🎬 1080p (Premium)", 'qaudio': "🎵 Faqat ovoz",
    },
    'ru': {
        'choose_lang':     "🌐 Выберите язык:",
        'lang_set':        "✅ Язык: Русский",
        'welcome':         "👋 Привет, *{name}*!\n\n🎬 Отправьте видео или ссылку YouTube/Instagram.\n\n📊 Тариф: *{plan}*\n📈 Сегодня: *{used}/{limit}*",
        'free_plan':       "🆓 Бесплатный",
        'premium_plan':    "⭐ Премиум",
        'limit_reached':   "❌ Дневной лимит (*{limit}*).\n\n⭐ Оформите Премиум — без ограничений!",
        'processing':      "⏳ Обрабатывается...",
        'downloading':     "⬇️ Загрузка...",
        'choose_quality':  "🎬 Выберите качество:\n_(Free: 360p или Аудио)_",
        'choose_quality_p':"🎬 Выберите качество:",
        'choose_action':   "✅ Видео загружено!\n⏱ Длительность: *{dur}*\n\nЧто хотите сделать?",
        'full_extract':    "▶️ Полный звук",
        'trim_audio':      "✂️ Обрезать",
        'enter_start':     "📍 *Введите время начала*:\n_Пример: `1:30` или `90`_\n\nДлительность: *{dur}*",
        'enter_end':       "📍 *Введите время конца*:\n_Пример: `3:00` или `180`_\n\nНачало: *{start}*",
        'invalid_time':    "❌ Неверный формат. Пример: `1:30` или `90`",
        'time_too_big':    "❌ Видео {dur}. Введите меньшее значение.",
        'end_less':        "❌ Время конца должно быть больше начала.",
        'voice_cap':       "🎤 Звук из видео",
        'voice_trim_cap':  "🎤 Обрезанный звук: {start} → {end}",
        'mp3_cap':         "🎵 MP3 файл",
        'mp3_trim_cap':    "🎵 Обрезанный MP3: {start}–{end}",
        'send_screenshot': "📸 Отправьте *скриншот* чека оплаты:",
        'screenshot_sent': "✅ Скриншот отправлен!\n⏳ Проверяется...",
        'pay_granted':     "🎉 *Поздравляем!*\n✅ Оплата подтверждена!\n⭐ *Премиум на {days} дней* активирован!\n📅 До *{until}*",
        'pay_rejected':    "❌ *Оплата не подтверждена.*\nПопробуйте снова.",
        'premium_info':    "⭐ *Премиум — {price}/мес*\n\n✅ Безлимитно\n✂️ Обрезка\n🔇 Шумоподавление\n📥 YouTube/Instagram (до 1080p)\n\n{pay_details}",
        'pay_details':     "💳 *Оплата:*\n🔵 Click: `+998901234567`\n🟢 Payme: `+998901234567`\n💳 Uzcard: `8600 0000 0000 0000`",
        'i_paid':          "✅ Я оплатил",
        'get_premium':     "⭐ Получить Премиум",
        'my_status':       "📊 Мой статус",
        'referral_btn':    "👥 Реферал",
        'referral_info':   "👥 *Реферальная программа*\n\nЗа каждого приглашённого *+{bonus} дней*!\n\n🔗 Ваша ссылка:\n`{link}`\n\n✅ Приглашено: *{count}*\n🎁 Бонусных дней: *{days}*",
        'ref_bonus':       "🎁 *{name}* присоединился по вашей ссылке!\n+{bonus} дней добавлено!",
        'no_video':        "❌ Видео не найдено. Отправьте снова.",
        'error':           "❌ Ошибка. Попробуйте снова.",
        'hint':            "🎬 Отправьте видео или ссылку!\n/start /premium /referral /language",
        'status_text':     "📊 *Статус:*\n\n👤 *{name}*\n🎯 Тариф: *{plan}*\n📈 Сегодня: *{used}/{limit}*\n📅 Премиум: *{until}*\n👥 Приглашено: *{refs}*",
        'prem_until':      "до {date}",
        'no_prem':         "Нет",
        'file_too_big':    "⚠️ Файл слишком большой ({size} MB). Telegram принимает до 50MB.",
        'noise_remove':    "🔇 Шумоподавление (Премиум)",
        'noise_done':      "🔇 Шум удалён!",
        'q360': "📱 360p", 'q480': "💻 480p (Премиум)", 'q720': "🖥 720p (Премиум)", 'q1080': "🎬 1080p (Премиум)", 'qaudio': "🎵 Только звук",
    },
    'en': {
        'choose_lang':     "🌐 Choose language:",
        'lang_set':        "✅ Language: English",
        'welcome':         "👋 Hello, *{name}*!\n\n🎬 Send a video or YouTube/Instagram link.\n\n📊 Plan: *{plan}*\n📈 Today: *{used}/{limit}*",
        'free_plan':       "🆓 Free",
        'premium_plan':    "⭐ Premium",
        'limit_reached':   "❌ Daily limit reached (*{limit}*).\n\n⭐ Get Premium — unlimited!",
        'processing':      "⏳ Processing...",
        'downloading':     "⬇️ Downloading...",
        'choose_quality':  "🎬 Choose quality:\n_(Free: 360p or Audio)_",
        'choose_quality_p':"🎬 Choose quality:",
        'choose_action':   "✅ Video loaded!\n⏱ Duration: *{dur}*\n\nWhat would you like to do?",
        'full_extract':    "▶️ Full audio",
        'trim_audio':      "✂️ Trim audio",
        'enter_start':     "📍 *Enter start time*:\n_Example: `1:30` or `90`_\n\nDuration: *{dur}*",
        'enter_end':       "📍 *Enter end time*:\n_Example: `3:00` or `180`_\n\nStart: *{start}*",
        'invalid_time':    "❌ Invalid format. Example: `1:30` or `90`",
        'time_too_big':    "❌ Video is {dur}. Enter a smaller value.",
        'end_less':        "❌ End time must be greater than start.",
        'voice_cap':       "🎤 Audio from video",
        'voice_trim_cap':  "🎤 Trimmed: {start} → {end}",
        'mp3_cap':         "🎵 MP3 file",
        'mp3_trim_cap':    "🎵 Trimmed MP3: {start}–{end}",
        'send_screenshot': "📸 Send *screenshot* of your payment receipt:",
        'screenshot_sent': "✅ Screenshot sent!\n⏳ Being reviewed...",
        'pay_granted':     "🎉 *Congratulations!*\n✅ Payment confirmed!\n⭐ *{days}-day Premium* activated!\n📅 Until *{until}*",
        'pay_rejected':    "❌ *Payment not confirmed.*\nPlease try again.",
        'premium_info':    "⭐ *Premium — {price}/month*\n\n✅ Unlimited\n✂️ Trim audio\n🔇 Noise removal\n📥 YouTube/Instagram (up to 1080p)\n\n{pay_details}",
        'pay_details':     "💳 *Payment:*\n🔵 Click: `+998901234567`\n🟢 Payme: `+998901234567`\n💳 Uzcard: `8600 0000 0000 0000`",
        'i_paid':          "✅ I paid",
        'get_premium':     "⭐ Get Premium",
        'my_status':       "📊 My status",
        'referral_btn':    "👥 Referral",
        'referral_info':   "👥 *Referral Program*\n\nGet *+{bonus} days* per referral!\n\n🔗 Your link:\n`{link}`\n\n✅ Referred: *{count}*\n🎁 Bonus days: *{days}*",
        'ref_bonus':       "🎁 *{name}* joined via your link!\n+{bonus} days added!",
        'no_video':        "❌ Video not found. Send again.",
        'error':           "❌ Error. Please try again.",
        'hint':            "🎬 Send a video or link!\n/start /premium /referral /language",
        'status_text':     "📊 *Status:*\n\n👤 *{name}*\n🎯 Plan: *{plan}*\n📈 Today: *{used}/{limit}*\n📅 Premium: *{until}*\n👥 Referred: *{refs}*",
        'prem_until':      "until {date}",
        'no_prem':         "None",
        'file_too_big':    "⚠️ File too large ({size} MB). Telegram accepts up to 50MB.",
        'noise_remove':    "🔇 Noise removal (Premium)",
        'noise_done':      "🔇 Noise removed!",
        'q360': "📱 360p", 'q480': "💻 480p (Premium)", 'q720': "🖥 720p (Premium)", 'q1080': "🎬 1080p (Premium)", 'qaudio': "🎵 Audio only",
    },
}

def tx(uid_or_lang, key, **kw):
    """Tarjima olish yordamchi funksiyasi."""
    lang = uid_or_lang if uid_or_lang in T else get_lang(uid_or_lang)
    text = T.get(lang, T['en']).get(key, T['en'].get(key, key))
    return text.format(**kw) if kw else text


# ╔══════════════════════════════════════════════════════════╗
#                      DATABASE
# ╚══════════════════════════════════════════════════════════╝
def init_db():
    with sqlite3.connect(DB_PATH) as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            user_id        INTEGER PRIMARY KEY,
            username       TEXT,
            first_name     TEXT,
            language       TEXT DEFAULT 'en',
            is_premium     INTEGER DEFAULT 0,
            premium_until  TEXT,
            purchase_count INTEGER DEFAULT 0,
            free_used      INTEGER DEFAULT 0,
            last_use_date  TEXT,
            last_activity  TEXT,
            referred_by    INTEGER DEFAULT 0,
            bonus_days     INTEGER DEFAULT 0,
            created_at     TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS payments (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id       INTEGER,
            screenshot_id TEXT,
            status        TEXT DEFAULT 'pending',
            created_at    TEXT DEFAULT (datetime('now'))
        );
        """)


def ensure_user(uid: int, username: str, first_name: str):
    with sqlite3.connect(DB_PATH) as c:
        c.execute("""
            INSERT INTO users (user_id, username, first_name)
            VALUES (?,?,?)
            ON CONFLICT(user_id) DO UPDATE SET
                username=excluded.username,
                first_name=excluded.first_name,
                last_activity=datetime('now')
        """, (uid, username or "", first_name or ""))


def get_user(uid: int):
    with sqlite3.connect(DB_PATH) as c:
        return c.execute("SELECT * FROM users WHERE user_id=?", (uid,)).fetchone()


def get_lang(uid: int) -> str:
    with sqlite3.connect(DB_PATH) as c:
        row = c.execute("SELECT language FROM users WHERE user_id=?", (uid,)).fetchone()
    return row[0] if row else 'en'


def set_lang(uid: int, lang: str):
    with sqlite3.connect(DB_PATH) as c:
        c.execute("UPDATE users SET language=? WHERE user_id=?", (lang, uid))


def is_premium(uid: int) -> bool:
    with sqlite3.connect(DB_PATH) as c:
        row = c.execute("SELECT is_premium, premium_until FROM users WHERE user_id=?", (uid,)).fetchone()
    if not row or not row[0] or not row[1]:
        return False
    return datetime.fromisoformat(row[1]) > datetime.now()


def get_premium_until(uid: int):
    with sqlite3.connect(DB_PATH) as c:
        row = c.execute("SELECT premium_until FROM users WHERE user_id=?", (uid,)).fetchone()
    return datetime.fromisoformat(row[0]) if (row and row[0]) else None


def grant_premium(uid: int, days: int = 30) -> datetime:
    cur  = get_premium_until(uid)
    base = cur if (cur and cur > datetime.now()) else datetime.now()
    until = base + timedelta(days=days)
    with sqlite3.connect(DB_PATH) as c:
        c.execute("""
            UPDATE users SET is_premium=1, premium_until=?,
            purchase_count=purchase_count+1 WHERE user_id=?
        """, (until.isoformat(), uid))
    return until


def check_daily_limit(uid: int) -> bool:
    """True = limit oshirilmagan (foydalanish mumkin)."""
    today = datetime.now().date().isoformat()
    with sqlite3.connect(DB_PATH) as c:
        row = c.execute("SELECT free_used, last_use_date FROM users WHERE user_id=?", (uid,)).fetchone()
    if not row:
        return True
    used, last = row
    if last != today:
        with sqlite3.connect(DB_PATH) as c:
            c.execute("UPDATE users SET free_used=0, last_use_date=? WHERE user_id=?", (today, uid))
        return True
    return used < FREE_DAILY_LIMIT


def increment_usage(uid: int):
    today = datetime.now().date().isoformat()
    with sqlite3.connect(DB_PATH) as c:
        c.execute("""
            UPDATE users SET free_used=free_used+1, last_use_date=?, last_activity=datetime('now')
            WHERE user_id=?
        """, (today, uid))


def get_used_today(uid: int) -> int:
    today = datetime.now().date().isoformat()
    with sqlite3.connect(DB_PATH) as c:
        row = c.execute("SELECT free_used, last_use_date FROM users WHERE user_id=?", (uid,)).fetchone()
    if not row:
        return 0
    used, last = row
    return used if last == today else 0


def add_payment(uid: int, file_id: str) -> int:
    with sqlite3.connect(DB_PATH) as c:
        cur = c.execute("INSERT INTO payments (user_id, screenshot_id) VALUES (?,?)", (uid, file_id))
        return cur.lastrowid


def set_payment_status(pid: int, status: str):
    with sqlite3.connect(DB_PATH) as c:
        c.execute("UPDATE payments SET status=? WHERE id=?", (status, pid))


def get_payment(pid: int):
    with sqlite3.connect(DB_PATH) as c:
        return c.execute("SELECT * FROM payments WHERE id=?", (pid,)).fetchone()


def get_referral_count(uid: int) -> int:
    with sqlite3.connect(DB_PATH) as c:
        row = c.execute("SELECT COUNT(*) FROM users WHERE referred_by=?", (uid,)).fetchone()
    return row[0] if row else 0


def add_bonus_days(uid: int, days: int):
    """Referral bonus — premium ga qo'shadi."""
    with sqlite3.connect(DB_PATH) as c:
        c.execute("UPDATE users SET bonus_days=bonus_days+? WHERE user_id=?", (days, uid))
    # Agar premium bo'lsa, muddatiga qo'shadi
    if is_premium(uid):
        until = get_premium_until(uid) + timedelta(days=days)
        with sqlite3.connect(DB_PATH) as c:
            c.execute("UPDATE users SET premium_until=? WHERE user_id=?", (until.isoformat(), uid))


def all_user_ids() -> list:
    with sqlite3.connect(DB_PATH) as c:
        return [r[0] for r in c.execute("SELECT user_id FROM users").fetchall()]


# ── Statistika ────────────────────────────────────────────
def get_stats() -> dict:
    now  = datetime.now()
    week = (now - timedelta(days=7)).isoformat()
    month= (now - timedelta(days=30)).isoformat()
    today= now.date().isoformat()

    with sqlite3.connect(DB_PATH) as c:
        total   = c.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        active  = c.execute("SELECT COUNT(*) FROM users WHERE last_activity>=?", (week,)).fetchone()[0]
        premium = c.execute(
            "SELECT COUNT(*) FROM users WHERE is_premium=1 AND premium_until>?",
            (now.isoformat(),)
        ).fetchone()[0]
        new_today = c.execute("SELECT COUNT(*) FROM users WHERE date(created_at)=?", (today,)).fetchone()[0]
        new_week  = c.execute("SELECT COUNT(*) FROM users WHERE created_at>=?", (week,)).fetchone()[0]
        new_month = c.execute("SELECT COUNT(*) FROM users WHERE created_at>=?", (month,)).fetchone()[0]
        pending_pays = c.execute("SELECT COUNT(*) FROM payments WHERE status='pending'").fetchone()[0]

    return {
        'total': total, 'active': active, 'inactive': total - active,
        'premium': premium, 'new_today': new_today,
        'new_week': new_week, 'new_month': new_month,
        'pending_pays': pending_pays,
    }


def get_premium_users_recent(limit=30) -> list:
    """So'nggi premium olganlar."""
    now = datetime.now().isoformat()
    with sqlite3.connect(DB_PATH) as c:
        return c.execute("""
            SELECT user_id, first_name, username, purchase_count, premium_until
            FROM users WHERE is_premium=1 AND premium_until>?
            ORDER BY premium_until DESC LIMIT ?
        """, (now, limit)).fetchall()


def get_premium_users_top(limit=30) -> list:
    """Eng ko'p premium olganlar."""
    now = datetime.now().isoformat()
    with sqlite3.connect(DB_PATH) as c:
        return c.execute("""
            SELECT user_id, first_name, username, purchase_count, premium_until
            FROM users WHERE purchase_count>0
            ORDER BY purchase_count DESC LIMIT ?
        """, (limit,)).fetchall()


# ╔══════════════════════════════════════════════════════════╗
#                    YORDAMCHI FUNKSIYALAR
# ╚══════════════════════════════════════════════════════════╝
def parse_time(text: str):
    try:
        text = text.strip()
        if ':' in text:
            p = text.split(':')
            if len(p) == 2:
                return int(p[0]) * 60 + float(p[1])
            if len(p) == 3:
                return int(p[0]) * 3600 + int(p[1]) * 60 + float(p[2])
        return float(text)
    except (ValueError, IndexError):
        return None


def fmt(sec) -> str:
    if sec is None:
        return "?"
    h, rem = divmod(int(sec), 3600)
    m, s   = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def get_duration(path: str):
    try:
        res = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", path],
            capture_output=True, text=True, check=True,
        )
        return float(res.stdout.strip())
    except Exception:
        return None


def file_size_mb(path: str) -> float:
    return os.path.getsize(path) / (1024 * 1024)


# ╔══════════════════════════════════════════════════════════╗
#               AUDIO / VIDEO QAYTA ISHLASH
# ╚══════════════════════════════════════════════════════════╝
async def send_audio_files(bot, chat_id: int, video_path: str,
                           start_sec=None, end_sec=None,
                           noise_remove: bool = False, lang: str = 'en'):
    """Video dan ovoz ajratib Voice + MP3 yuboradi."""
    base     = f"{chat_id}_{os.path.splitext(os.path.basename(video_path))[0]}"
    ogg_path = os.path.join(TEMP_DIR, f"{base}.ogg")
    mp3_path = os.path.join(TEMP_DIR, f"{base}.mp3")

    trim = []
    if start_sec is not None:
        trim += ["-ss", str(start_sec)]
        if end_sec is not None:
            trim += ["-t", str(end_sec - start_sec)]

    noise_filter = ["-af", "afftdn=nf=-25"] if noise_remove else []

    for codec, extra, out in [
        ("libopus",    ["-ar","48000","-ac","1","-b:a","64k"],  ogg_path),
        ("libmp3lame", ["-ar","44100","-ac","2","-b:a","192k"], mp3_path),
    ]:
        subprocess.run(
            ["ffmpeg", "-y", "-i", video_path] + trim + noise_filter +
            ["-vn", "-acodec", codec] + extra + [out],
            check=True, capture_output=True,
        )

    if start_sec is not None:
        cap_v = tx(lang, 'voice_trim_cap', start=fmt(start_sec), end=fmt(end_sec))
        cap_a = tx(lang, 'mp3_trim_cap',   start=fmt(start_sec), end=fmt(end_sec))
    else:
        cap_v = tx(lang, 'voice_cap')
        cap_a = tx(lang, 'mp3_cap')

    if noise_remove:
        cap_v += "\n🔇"
        cap_a += " 🔇"

    with open(ogg_path, 'rb') as f:
        await bot.send_voice(chat_id, voice=f, caption=cap_v)
    with open(mp3_path, 'rb') as f:
        await bot.send_audio(chat_id, audio=f, caption=cap_a,
                             filename=f"audio_{base}.mp3")

    for p in (ogg_path, mp3_path):
        if os.path.exists(p):
            os.remove(p)


def download_yt(url: str, quality: str, out_path: str) -> str:
    """yt-dlp bilan yuklab oladi. Yakuniy fayl yo'lini qaytaradi."""
    fmt_map = {
        '360':   'bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/best[height<=360][ext=mp4]/best[height<=360]',
        '480':   'bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480]',
        '720':   'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720]',
        '1080':  'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080]',
        'audio': 'bestaudio/best',
    }
    ydl_opts = {
        'format':           fmt_map.get(quality, 'best'),
        'outtmpl':          out_path,
        'quiet':            True,
        'no_warnings':      True,
        'merge_output_format': 'mp4',
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }] if quality != 'audio' else [],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    # Fayl nomini topish (.mp4 yoki .webm)
    for ext in ('mp4', 'webm', 'mkv', 'm4a', 'mp3', 'ogg'):
        candidate = out_path.replace('%(ext)s', ext)
        if os.path.exists(candidate):
            return candidate
    # Agar ext to'g'ridan-to'g'ri yo'l bo'lsa
    if os.path.exists(out_path):
        return out_path
    raise FileNotFoundError("Yuklab olingan fayl topilmadi")


# ╔══════════════════════════════════════════════════════════╗
#                  ADMIN PANEL KEYBOARD
# ╚══════════════════════════════════════════════════════════╝
ADMIN_KB = RKM([
    [KB("📊 Statistika"),        KB("📢 Xabar yuborish")],
    [KB("👑 Yaqinda premium"),   KB("🏆 Ko'p sotib olgan")],
    [KB("✅ Premium berish"),    KB("❌ Premium olish")],
    [KB("📋 Kutayotgan to'lovlar")],
], resize_keyboard=True)


# ╔══════════════════════════════════════════════════════════╗
#                  FOYDALANUVCHI HANDLERLARI
# ╚══════════════════════════════════════════════════════════╝

# ── /start ────────────────────────────────────────────────
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u    = update.effective_user
    args = context.args

    ensure_user(u.id, u.username, u.first_name)

    # Referal tekshirish
    if args and args[0].startswith("ref_"):
        try:
            ref_id = int(args[0][4:])
            if ref_id != u.id:
                row = get_user(u.id)
                if row and row[10] == 0:  # referred_by == 0
                    with sqlite3.connect(DB_PATH) as c:
                        c.execute("UPDATE users SET referred_by=? WHERE user_id=?", (ref_id, u.id))
                    add_bonus_days(ref_id, REFERRAL_BONUS)
                    ref_row = get_user(ref_id)
                    if ref_row:
                        await context.bot.send_message(
                            ref_id,
                            tx(get_lang(ref_id), 'ref_bonus',
                               name=u.first_name, bonus=REFERRAL_BONUS),
                            parse_mode="Markdown",
                        )
        except (ValueError, TypeError):
            pass

    # Admin uchun reply keyboard
    if u.id in ADMIN_IDS:
        await update.message.reply_text(
            f"👑 Admin panel\n\n👤 {u.first_name}",
            reply_markup=ADMIN_KB,
        )
        return

    # Yangi foydalanuvchi → til tanlash
    row = get_user(u.id)
    if row and row[3] == 'en' and not args:
        # Til tanlash so'rash (birinchi marta)
        kb = IKM([[
            IKB("🇺🇿 O'zbek", callback_data="lang_uz"),
            IKB("🇷🇺 Русский", callback_data="lang_ru"),
            IKB("🇬🇧 English", callback_data="lang_en"),
        ]])
        await update.message.reply_text(
            T['uz']['choose_lang'], reply_markup=kb
        )
        return

    await show_welcome(update, context)


async def show_welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u    = update.effective_user
    lang = get_lang(u.id)
    prem = is_premium(u.id)
    used = get_used_today(u.id)
    plan = tx(lang, 'premium_plan') if prem else tx(lang, 'free_plan')
    lim  = "∞" if prem else str(FREE_DAILY_LIMIT)

    kb = IKM([
        [IKB(tx(lang, 'get_premium'), callback_data="show_premium"),
         IKB(tx(lang, 'my_status'),   callback_data="my_status")],
        [IKB(tx(lang, 'referral_btn'), callback_data="referral")],
    ])
    await update.message.reply_text(
        tx(lang, 'welcome', name=u.first_name, plan=plan, used=used, limit=lim),
        parse_mode="Markdown", reply_markup=kb,
    )


# ── /language ─────────────────────────────────────────────
async def cmd_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id in ADMIN_IDS:
        return
    kb = IKM([[
        IKB("🇺🇿 O'zbek", callback_data="lang_uz"),
        IKB("🇷🇺 Русский", callback_data="lang_ru"),
        IKB("🇬🇧 English", callback_data="lang_en"),
    ]])
    await update.message.reply_text(T['uz']['choose_lang'], reply_markup=kb)


# ── /premium ──────────────────────────────────────────────
async def cmd_premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id in ADMIN_IDS:
        return
    await _show_premium_info(update.message, update.effective_user.id)


# ── /referral ─────────────────────────────────────────────
async def cmd_referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id in ADMIN_IDS:
        return
    await _show_referral(update.message, update.effective_user.id)


async def _show_premium_info(message, uid: int):
    lang = get_lang(uid)
    kb   = IKM([[IKB(tx(lang, 'i_paid'), callback_data="i_paid")]])
    await message.reply_text(
        tx(lang, 'premium_info',
           price=PREMIUM_PRICE,
           pay_details=tx(lang, 'pay_details')),
        parse_mode="Markdown", reply_markup=kb,
    )


async def _show_referral(message, uid: int):
    lang  = get_lang(uid)
    count = get_referral_count(uid)
    row   = get_user(uid)
    bonus = row[11] if row else 0
    link  = f"https://t.me/{BOT_USERNAME}?start=ref_{uid}"
    await message.reply_text(
        tx(lang, 'referral_info',
           bonus=REFERRAL_BONUS, link=link, count=count, days=bonus),
        parse_mode="Markdown",
    )


# ── VIDEO handler ─────────────────────────────────────────
async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u   = update.effective_user
    if u.id in ADMIN_IDS:
        return
    msg = update.message
    lang = get_lang(u.id)

    prem = is_premium(u.id)
    if not prem and not check_daily_limit(u.id):
        used = get_used_today(u.id)
        await msg.reply_text(
            tx(lang, 'limit_reached', limit=FREE_DAILY_LIMIT),
            parse_mode="Markdown",
            reply_markup=IKM([[IKB(tx(lang, 'get_premium'), callback_data="show_premium")]]),
        )
        return

    if msg.video:
        file  = msg.video
        fname = f"v_{u.id}_{file.file_unique_id}.mp4"
    elif msg.video_note:
        file  = msg.video_note
        fname = f"vn_{u.id}_{file.file_unique_id}.mp4"
    elif msg.document and msg.document.mime_type and msg.document.mime_type.startswith("video/"):
        file  = msg.document
        fname = f"doc_{u.id}_{file.file_unique_id}.mp4"
    else:
        return

    video_path = os.path.join(TEMP_DIR, fname)
    status     = await msg.reply_text(tx(lang, 'processing'))

    try:
        tg_file = await context.bot.get_file(file.file_id)
        await tg_file.download_to_drive(video_path)
    except Exception as e:
        await status.edit_text(tx(lang, 'error'))
        return

    duration = get_duration(video_path)

    if prem:
        context.user_data.update({'video_path': video_path, 'video_dur': duration})
        kb = IKM([
            [IKB(tx(lang, 'full_extract'),  callback_data="full_extract")],
            [IKB(tx(lang, 'trim_audio'),    callback_data="trim_audio")],
            [IKB(tx(lang, 'noise_remove'),  callback_data="noise_remove")],
        ])
        await status.edit_text(
            tx(lang, 'choose_action', dur=fmt(duration)),
            parse_mode="Markdown", reply_markup=kb,
        )
    else:
        # Bepul: to'liq extract
        await status.edit_text(tx(lang, 'processing'))
        try:
            await send_audio_files(context.bot, u.id, video_path, lang=lang)
            increment_usage(u.id)
            await status.delete()
        except subprocess.CalledProcessError:
            await status.edit_text(tx(lang, 'error'))
        finally:
            if os.path.exists(video_path):
                os.remove(video_path)


# ── RASM handler (payment screenshot) ────────────────────
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u    = update.effective_user
    if u.id in ADMIN_IDS:
        return
    lang = get_lang(u.id)

    if not context.user_data.get('awaiting_screenshot'):
        return

    context.user_data.pop('awaiting_screenshot', None)
    file_id    = update.message.photo[-1].file_id
    payment_id = add_payment(u.id, file_id)

    admin_kb = IKM([[
        IKB("✅ Tasdiqlash", callback_data=f"approve_{payment_id}"),
        IKB("❌ Rad etish",  callback_data=f"reject_{payment_id}"),
    ]])
    caption = (
        f"💳 *Yangi to'lov #{payment_id}*\n\n"
        f"👤 [{u.first_name}](tg://user?id={u.id})\n"
        f"🆔 `{u.id}`\n"
        f"📌 @{u.username or '—'}\n"
        f"🕐 {datetime.now().strftime('%d.%m.%Y %H:%M')}"
    )
    for admin_id in ADMIN_IDS:
        try:
            await context.bot.send_photo(
                admin_id, photo=file_id,
                caption=caption, parse_mode="Markdown",
                reply_markup=admin_kb,
            )
        except Exception as e:
            logger.error("Admin ga yuborishda xatolik: %s", e)

    await update.message.reply_text(
        tx(lang, 'screenshot_sent'), parse_mode="Markdown"
    )


# ── MATN handler (trim vaqtlari + URL) ────────────────────
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u    = update.effective_user
    text = update.message.text or ""
    lang = get_lang(u.id)

    # ── ADMIN panel ──────────────────────────────────────
    if u.id in ADMIN_IDS:
        await handle_admin_text(update, context, text)
        return

    # ── YouTube / Instagram URL ──────────────────────────
    if YT_RE.match(text.strip()):
        await handle_url(update, context, text.strip())
        return

    # ── Trim boshlanish vaqti ────────────────────────────
    if context.user_data.get('awaiting_trim_start'):
        sec = parse_time(text)
        dur = context.user_data.get('video_dur', 0)
        if sec is None:
            await update.message.reply_text(tx(lang, 'invalid_time'), parse_mode="Markdown")
            return
        if dur and sec >= dur:
            await update.message.reply_text(tx(lang, 'time_too_big', dur=fmt(dur)), parse_mode="Markdown")
            return
        context.user_data.pop('awaiting_trim_start', None)
        context.user_data['trim_start']       = sec
        context.user_data['awaiting_trim_end'] = True
        await update.message.reply_text(
            tx(lang, 'enter_end', start=fmt(sec)),
            parse_mode="Markdown",
        )
        return

    # ── Trim tugash vaqti ────────────────────────────────
    if context.user_data.get('awaiting_trim_end'):
        sec   = parse_time(text)
        start = context.user_data.get('trim_start', 0)
        dur   = context.user_data.get('video_dur', 0)
        vpath = context.user_data.get('video_path')
        noise = context.user_data.get('noise_remove', False)

        if sec is None:
            await update.message.reply_text(tx(lang, 'invalid_time'), parse_mode="Markdown")
            return
        if sec <= start:
            await update.message.reply_text(tx(lang, 'end_less'), parse_mode="Markdown")
            return
        if dur and sec > dur:
            await update.message.reply_text(tx(lang, 'time_too_big', dur=fmt(dur)), parse_mode="Markdown")
            return
        if not vpath or not os.path.exists(vpath):
            await update.message.reply_text(tx(lang, 'no_video'))
            context.user_data.clear()
            return

        for k in ('awaiting_trim_end', 'trim_start', 'video_path', 'video_dur', 'noise_remove'):
            context.user_data.pop(k, None)

        status = await update.message.reply_text(tx(lang, 'processing'))
        try:
            await send_audio_files(context.bot, u.id, vpath,
                                   start_sec=start, end_sec=sec,
                                   noise_remove=noise, lang=lang)
            increment_usage(u.id)
            await status.delete()
        except subprocess.CalledProcessError:
            await status.edit_text(tx(lang, 'error'))
        finally:
            if os.path.exists(vpath):
                os.remove(vpath)
        return

    # ── Screenshot kutilmoqda ────────────────────────────
    if context.user_data.get('awaiting_screenshot'):
        await update.message.reply_text(
            tx(lang, 'send_screenshot'), parse_mode="Markdown"
        )
        return

    # ── Boshqa ──────────────────────────────────────────
    await update.message.reply_text(tx(lang, 'hint'))


# ── YouTube / Instagram ───────────────────────────────────
async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE, url: str):
    u    = update.effective_user
    lang = get_lang(u.id)
    prem = is_premium(u.id)

    if not prem and not check_daily_limit(u.id):
        await update.message.reply_text(
            tx(lang, 'limit_reached', limit=FREE_DAILY_LIMIT),
            parse_mode="Markdown",
            reply_markup=IKM([[IKB(tx(lang, 'get_premium'), callback_data="show_premium")]]),
        )
        return

    context.user_data['yt_url'] = url
    qkey = 'choose_quality_p' if prem else 'choose_quality'

    if prem:
        kb = IKM([
            [IKB(tx(lang, 'q360'),   callback_data="yt_360"),
             IKB(tx(lang, 'q480'),   callback_data="yt_480")],
            [IKB(tx(lang, 'q720'),   callback_data="yt_720"),
             IKB(tx(lang, 'q1080'),  callback_data="yt_1080")],
            [IKB(tx(lang, 'qaudio'), callback_data="yt_audio")],
        ])
    else:
        kb = IKM([
            [IKB(tx(lang, 'q360'),   callback_data="yt_360")],
            [IKB(tx(lang, 'qaudio'), callback_data="yt_audio")],
        ])

    await update.message.reply_text(
        tx(lang, qkey), parse_mode="Markdown", reply_markup=kb
    )


# ── CALLBACK handler ──────────────────────────────────────
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q    = update.callback_query
    data = q.data
    u    = q.from_user
    lang = get_lang(u.id)
    await q.answer()

    # ── Til tanlash ─────────────────────────────────────
    if data.startswith("lang_"):
        new_lang = data[5:]
        set_lang(u.id, new_lang)
        await q.message.edit_text(T[new_lang]['lang_set'])
        await show_welcome_cb(q, u, new_lang)
        return

    # ── Premium info ─────────────────────────────────────
    if data == "show_premium":
        await _show_premium_info(q.message, u.id)
        return

    # ── My status ────────────────────────────────────────
    if data == "my_status":
        prem = is_premium(u.id)
        row  = get_user(u.id)
        used = get_used_today(u.id)
        plan = tx(lang, 'premium_plan') if prem else tx(lang, 'free_plan')
        lim  = "∞" if prem else str(FREE_DAILY_LIMIT)
        until_txt = tx(lang, 'prem_until', date=get_premium_until(u.id).strftime('%d.%m.%Y')) if prem else tx(lang, 'no_prem')
        refs  = get_referral_count(u.id)
        await q.message.reply_text(
            tx(lang, 'status_text', name=u.first_name, plan=plan,
               used=used, limit=lim, until=until_txt, refs=refs),
            parse_mode="Markdown",
        )
        return

    # ── Referral ──────────────────────────────────────────
    if data == "referral":
        await _show_referral(q.message, u.id)
        return

    # ── To'lov qildim ────────────────────────────────────
    if data == "i_paid":
        context.user_data['awaiting_screenshot'] = True
        await q.message.reply_text(
            tx(lang, 'send_screenshot'), parse_mode="Markdown"
        )
        return

    # ── To'liq extract (premium) ─────────────────────────
    if data == "full_extract":
        vpath = context.user_data.pop('video_path', None)
        dur   = context.user_data.pop('video_dur',  None)
        if not vpath or not os.path.exists(vpath):
            await q.message.reply_text(tx(lang, 'no_video'))
            return
        await q.message.edit_text(tx(lang, 'processing'))
        try:
            await send_audio_files(context.bot, u.id, vpath, lang=lang)
            increment_usage(u.id)
            await q.message.delete()
        except subprocess.CalledProcessError:
            await q.message.edit_text(tx(lang, 'error'))
        finally:
            if os.path.exists(vpath):
                os.remove(vpath)
        return

    # ── Shovqin yo'qotish ─────────────────────────────────
    if data == "noise_remove":
        context.user_data['noise_remove']    = True
        context.user_data['awaiting_trim_start'] = False
        vpath = context.user_data.get('video_path')
        dur   = context.user_data.get('video_dur')
        if not vpath or not os.path.exists(vpath):
            await q.message.reply_text(tx(lang, 'no_video'))
            return
        await q.message.edit_text(tx(lang, 'processing'))
        try:
            await send_audio_files(context.bot, u.id, vpath,
                                   noise_remove=True, lang=lang)
            increment_usage(u.id)
            context.user_data.pop('video_path', None)
            context.user_data.pop('video_dur', None)
            await q.message.delete()
        except subprocess.CalledProcessError:
            await q.message.edit_text(tx(lang, 'error'))
        finally:
            if os.path.exists(vpath):
                os.remove(vpath)
        return

    # ── Kesish (trim) ─────────────────────────────────────
    if data == "trim_audio":
        dur = context.user_data.get('video_dur')
        context.user_data['awaiting_trim_start'] = True
        await q.message.edit_text(
            tx(lang, 'enter_start', dur=fmt(dur)),
            parse_mode="Markdown",
        )
        return

    # ── YouTube sifat tanlash ─────────────────────────────
    if data.startswith("yt_"):
        quality = data[3:]
        url     = context.user_data.pop('yt_url', None)
        if not url:
            await q.message.edit_text(tx(lang, 'error'))
            return

        prem = is_premium(u.id)
        # Bepul foydalanuvchi faqat 360p va audio
        if not prem and quality not in ('360', 'audio'):
            await q.message.edit_text(
                tx(lang, 'limit_reached', limit=FREE_DAILY_LIMIT),
                parse_mode="Markdown",
                reply_markup=IKM([[IKB(tx(lang, 'get_premium'), callback_data="show_premium")]]),
            )
            return

        await q.message.edit_text(tx(lang, 'downloading'))

        out_template = os.path.join(TEMP_DIR, f"yt_{u.id}_{quality}.%(ext)s")
        try:
            loop    = asyncio.get_event_loop()
            dl_path = await loop.run_in_executor(
                None, download_yt, url, quality, out_template
            )
        except Exception as e:
            logger.error("YT download xatolik: %s", e)
            await q.message.edit_text(tx(lang, 'error'))
            return

        # Hajm tekshirish
        size_mb = file_size_mb(dl_path)
        if size_mb > MAX_TG_SIZE_MB:
            await q.message.edit_text(
                tx(lang, 'file_too_big', size=round(size_mb, 1))
            )
            if os.path.exists(dl_path):
                os.remove(dl_path)
            return

        await q.message.edit_text(tx(lang, 'processing'))

        try:
            if quality != 'audio':
                # Video yuborish
                with open(dl_path, 'rb') as f:
                    await context.bot.send_video(
                        u.id, video=f,
                        caption=f"🎬 {quality}p",
                        supports_streaming=True,
                    )
            # Har doim voice + mp3 ham yuborish
            await send_audio_files(context.bot, u.id, dl_path, lang=lang)
            increment_usage(u.id)
            await q.message.delete()
        except Exception as e:
            logger.error("Yuborishda xatolik: %s", e)
            await q.message.edit_text(tx(lang, 'error'))
        finally:
            if os.path.exists(dl_path):
                os.remove(dl_path)
        return

    # ── Admin: Tasdiqlash ─────────────────────────────────
    if data.startswith("approve_"):
        pid  = int(data.split("_")[1])
        pay  = get_payment(pid)
        if not pay:
            await q.message.reply_text("❌ To'lov topilmadi.")
            return
        tid   = pay[1]
        set_payment_status(pid, "approved")
        until = grant_premium(tid, PREMIUM_DAYS)
        await context.bot.send_message(
            tid,
            tx(get_lang(tid), 'pay_granted',
               days=PREMIUM_DAYS, until=until.strftime('%d.%m.%Y')),
            parse_mode="Markdown",
        )
        new_cap = (q.message.caption or "") + \
                  f"\n\n✅ TASDIQLANDI — {u.first_name} {datetime.now().strftime('%H:%M')}"
        await q.message.edit_caption(new_cap, parse_mode="Markdown")
        return

    # ── Admin: Rad etish ──────────────────────────────────
    if data.startswith("reject_"):
        pid = int(data.split("_")[1])
        pay = get_payment(pid)
        if not pay:
            await q.message.reply_text("❌ To'lov topilmadi.")
            return
        tid = pay[1]
        set_payment_status(pid, "rejected")
        await context.bot.send_message(
            tid,
            tx(get_lang(tid), 'pay_rejected'),
            parse_mode="Markdown",
        )
        new_cap = (q.message.caption or "") + \
                  f"\n\n❌ RAD ETILDI — {u.first_name} {datetime.now().strftime('%H:%M')}"
        await q.message.edit_caption(new_cap, parse_mode="Markdown")
        return


async def show_welcome_cb(q, u, lang):
    prem = is_premium(u.id)
    used = get_used_today(u.id)
    plan = tx(lang, 'premium_plan') if prem else tx(lang, 'free_plan')
    lim  = "∞" if prem else str(FREE_DAILY_LIMIT)
    kb   = IKM([
        [IKB(tx(lang, 'get_premium'), callback_data="show_premium"),
         IKB(tx(lang, 'my_status'),   callback_data="my_status")],
        [IKB(tx(lang, 'referral_btn'), callback_data="referral")],
    ])
    await q.message.reply_text(
        tx(lang, 'welcome', name=u.first_name, plan=plan, used=used, limit=lim),
        parse_mode="Markdown", reply_markup=kb,
    )


# ╔══════════════════════════════════════════════════════════╗
#                    ADMIN PANEL
# ╚══════════════════════════════════════════════════════════╝
async def handle_admin_text(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
    u = update.effective_user

    # ── Broadcast xabar olish ────────────────────────────
    if context.user_data.get('awaiting_broadcast'):
        context.user_data.pop('awaiting_broadcast', None)
        context.user_data['broadcast_msg'] = update.message
        await update.message.reply_text(
            f"📢 *Xabar yuborilsinmi?*\n\nJami: *{len(all_user_ids())}* ta foydalanuvchi",
            parse_mode="Markdown",
            reply_markup=RKM([[KB("✅ Ha, yubor"), KB("❌ Bekor qilish")]], resize_keyboard=True),
        )
        return

    if context.user_data.get('broadcast_msg'):
        if text == "✅ Ha, yubor":
            msg     = context.user_data.pop('broadcast_msg', None)
            uids    = all_user_ids()
            success = 0
            for uid in uids:
                try:
                    await msg.forward(uid)
                    success += 1
                    await asyncio.sleep(0.05)
                except Exception:
                    pass
            await update.message.reply_text(
                f"✅ Yuborildi: *{success}/{len(uids)}* ta",
                parse_mode="Markdown", reply_markup=ADMIN_KB,
            )
        else:
            context.user_data.pop('broadcast_msg', None)
            await update.message.reply_text("❌ Bekor qilindi.", reply_markup=ADMIN_KB)
        return

    # ── Premium berish ────────────────────────────────────
    if context.user_data.get('awaiting_grant_id'):
        context.user_data.pop('awaiting_grant_id', None)
        try:
            target_id = int(text.strip())
            until     = grant_premium(target_id, PREMIUM_DAYS)
            await update.message.reply_text(
                f"✅ Premium berildi!\n🆔 `{target_id}`\n📅 {until.strftime('%d.%m.%Y')} gacha",
                parse_mode="Markdown", reply_markup=ADMIN_KB,
            )
            tl = get_lang(target_id)
            await context.bot.send_message(
                target_id,
                tx(tl, 'pay_granted', days=PREMIUM_DAYS, until=until.strftime('%d.%m.%Y')),
                parse_mode="Markdown",
            )
        except (ValueError, Exception) as e:
            await update.message.reply_text(f"❌ Xatolik: {e}", reply_markup=ADMIN_KB)
        return

    # ── Premium olish (bekor qilish) ──────────────────────
    if context.user_data.get('awaiting_revoke_id'):
        context.user_data.pop('awaiting_revoke_id', None)
        try:
            target_id = int(text.strip())
            with sqlite3.connect(DB_PATH) as c:
                c.execute("UPDATE users SET is_premium=0, premium_until=NULL WHERE user_id=?", (target_id,))
            await update.message.reply_text(
                f"✅ Premium bekor qilindi. ID: `{target_id}`",
                parse_mode="Markdown", reply_markup=ADMIN_KB,
            )
        except (ValueError, Exception) as e:
            await update.message.reply_text(f"❌ Xatolik: {e}", reply_markup=ADMIN_KB)
        return

    # ── Reply keyboard tugmalari ──────────────────────────
    if text == "📊 Statistika":
        s = get_stats()
        await update.message.reply_text(
            f"📊 *BOT STATISTIKASI*\n\n"
            f"👥 Jami foydalanuvchilar: *{s['total']}*\n"
            f"🟢 Aktiv (7 kun): *{s['active']}*\n"
            f"🔴 Nofaol: *{s['inactive']}*\n"
            f"⭐ Premium: *{s['premium']}*\n\n"
            f"📅 Bugun yangi: *{s['new_today']}*\n"
            f"📅 Hafta: *{s['new_week']}*\n"
            f"📅 Oy: *{s['new_month']}*\n\n"
            f"💳 Kutayotgan to'lovlar: *{s['pending_pays']}*",
            parse_mode="Markdown", reply_markup=ADMIN_KB,
        )

    elif text == "📢 Xabar yuborish":
        context.user_data['awaiting_broadcast'] = True
        await update.message.reply_text(
            "📢 *Barcha foydalanuvchilarga yubormoqchi bo'lgan xabarni yuboring:*\n\n"
            "_(Matn, rasm, video — istalgan narsa)_",
            parse_mode="Markdown",
            reply_markup=RKM([[KB("❌ Bekor qilish")]], resize_keyboard=True),
        )

    elif text == "👑 Yaqinda premium":
        users = get_premium_users_recent(30)
        if not users:
            await update.message.reply_text("Premium foydalanuvchilar yo'q.", reply_markup=ADMIN_KB)
            return
        lines = ["👑 *Yaqinda premium olganlar:*\n"]
        for row in users:
            uid, fname, uname, count, until = row
            until_dt = datetime.fromisoformat(until).strftime('%d.%m.%Y') if until else "?"
            lines.append(
                f"• [{fname}](tg://user?id={uid}) @{uname or '—'}\n"
                f"  🛒 {count}x | 📅 {until_dt} gacha"
            )
        # 4096 belgi limitini hisobga olib, bo'lib yuborish
        await send_long_message(update.message, "\n".join(lines), ADMIN_KB)

    elif text == "🏆 Ko'p sotib olgan":
        users = get_premium_users_top(30)
        if not users:
            await update.message.reply_text("Ma'lumot yo'q.", reply_markup=ADMIN_KB)
            return
        lines = ["🏆 *Eng ko'p premium olganlar:*\n"]
        for i, row in enumerate(users, 1):
            uid, fname, uname, count, until = row
            lines.append(
                f"{i}. [{fname}](tg://user?id={uid}) @{uname or '—'} — *{count}x*"
            )
        await send_long_message(update.message, "\n".join(lines), ADMIN_KB)

    elif text == "✅ Premium berish":
        context.user_data['awaiting_grant_id'] = True
        await update.message.reply_text(
            "🆔 *Premium bermoqchi bo'lgan foydalanuvchining ID sini yuboring:*",
            parse_mode="Markdown",
        )

    elif text == "❌ Premium olish":
        context.user_data['awaiting_revoke_id'] = True
        await update.message.reply_text(
            "🆔 *Premium bekor qilmoqchi bo'lgan foydalanuvchining ID sini yuboring:*",
            parse_mode="Markdown",
        )

    elif text == "📋 Kutayotgan to'lovlar":
        with sqlite3.connect(DB_PATH) as c:
            rows = c.execute("""
                SELECT p.id, p.user_id, u.first_name, u.username, p.created_at
                FROM payments p LEFT JOIN users u ON p.user_id=u.user_id
                WHERE p.status='pending' ORDER BY p.created_at DESC LIMIT 20
            """).fetchall()
        if not rows:
            await update.message.reply_text("✅ Kutayotgan to'lovlar yo'q.", reply_markup=ADMIN_KB)
            return
        lines = ["📋 *Kutayotgan to'lovlar:*\n"]
        for row in rows:
            pid, uid, fname, uname, date_str = row
            lines.append(f"• #{pid} [{fname}](tg://user?id={uid}) — {date_str[:16]}")
        await send_long_message(update.message, "\n".join(lines), ADMIN_KB)

    else:
        await update.message.reply_text("👑 Admin panel:", reply_markup=ADMIN_KB)


async def send_long_message(message, text: str, kb, max_len: int = 4000):
    """Uzun xabarni bo'lib yuboradi."""
    if len(text) <= max_len:
        await message.reply_text(text, parse_mode="Markdown", reply_markup=kb)
        return
    parts = []
    while text:
        parts.append(text[:max_len])
        text = text[max_len:]
    for i, part in enumerate(parts):
        await message.reply_text(
            part,
            parse_mode="Markdown",
            reply_markup=kb if i == len(parts) - 1 else None,
        )


# ╔══════════════════════════════════════════════════════════╗
#                        MAIN
# ╚══════════════════════════════════════════════════════════╝
def main():
    init_db()
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start",    cmd_start))
    app.add_handler(CommandHandler("premium",  cmd_premium))
    app.add_handler(CommandHandler("referral", cmd_referral))
    app.add_handler(CommandHandler("language", cmd_language))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(
        filters.VIDEO | filters.VIDEO_NOTE |
        (filters.Document.MimeType("video/mp4") | filters.Document.MimeType("video/webm")),
        handle_video,
    ))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    logger.info("🚀 VTVS Bot v2.0 ishga tushdi!")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
