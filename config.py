"""
⚙️ VTVS Bot — Sozlamalar
Faqat shu faylni o'zgartirasiz, boshqa fayllarni tegmaysiz.
"""
import os

# ── Asosiy ────────────────────────────────────────────────
BOT_TOKEN        = os.getenv("BOT_TOKEN", "8229173995:AAH3JMphJYqsxk8xotgyUdEfqKzyCdl7jSo")
BOT_USERNAME     = "abdulhamidbot"   # @ siz (t.me/...)
ADMIN_IDS        = [5016497622]           # Bir nechta admin: [111, 222, 333]

# ── Fayllar ───────────────────────────────────────────────
TEMP_DIR         = "temp"
DB_PATH          = "vtvs.db"

# ── Premium ───────────────────────────────────────────────
PREMIUM_DAYS     = 30
PREMIUM_PRICE    = "$3"
STARS_AMOUNT     = 150        # Telegram Stars narxi
FREE_DAILY_LIMIT = 5          # Bepul kunlik limit
REFERRAL_BONUS   = 3          # Referal uchun bonus (kun)

# ── Texnik ────────────────────────────────────────────────
MAX_TG_MB        = 49         # Telegram fayl hajmi limiti
MAX_ALBUM        = 10         # Reklama albomida max media soni

# ── Scheduler (UTC vaqtida) ───────────────────────────────
DAILY_STATS_HOUR  = 7         # Kunlik statistika soati
EXPIRY_CHECK_HOUR = 8         # Premium tugash tekshiruvi
WEEKLY_STATS_DAY  = 0         # Haftalik statistika (0=Dushanba)

# ── Vocal isolation ───────────────────────────────────────
# True=demucs (sifatli, lekin sekin), False=ffmpeg (tez, taxminiy)
USE_DEMUCS = False

os.makedirs(TEMP_DIR, exist_ok=True)
