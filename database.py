"""
🗄 VTVS Bot — Database
SQLite asosida barcha ma'lumotlar saqlanadi.
"""
import json
import sqlite3
from datetime import datetime, timedelta
from config import DB_PATH, PREMIUM_DAYS, REFERRAL_BONUS


# ════════════════════════════════════════════════════════
#  INIT
# ════════════════════════════════════════════════════════
def init_db():
    with _db() as c:
        c.executescript("""
        -- Foydalanuvchilar
        CREATE TABLE IF NOT EXISTS users (
            user_id         INTEGER PRIMARY KEY,
            username        TEXT    DEFAULT '',
            first_name      TEXT    DEFAULT '',
            bot_language    TEXT    DEFAULT 'en',
            tg_language     TEXT    DEFAULT '',
            is_premium      INTEGER DEFAULT 0,
            premium_until   TEXT    DEFAULT '',
            purchase_count  INTEGER DEFAULT 0,
            free_used       INTEGER DEFAULT 0,
            last_use_date   TEXT    DEFAULT '',
            last_activity   TEXT    DEFAULT (datetime('now')),
            referred_by     INTEGER DEFAULT 0,
            bonus_days      INTEGER DEFAULT 0,
            total_processed INTEGER DEFAULT 0,
            is_banned       INTEGER DEFAULT 0,
            ban_reason      TEXT    DEFAULT '',
            created_at      TEXT    DEFAULT (datetime('now'))
        );

        -- To'lovlar (screenshot va Stars)
        CREATE TABLE IF NOT EXISTS payments (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id         INTEGER,
            pay_type        TEXT    DEFAULT 'screenshot',
            screenshot_id   TEXT    DEFAULT '',
            stars_charge_id TEXT    DEFAULT '',
            amount_stars    INTEGER DEFAULT 0,
            status          TEXT    DEFAULT 'pending',
            created_at      TEXT    DEFAULT (datetime('now'))
        );

        -- Promo kodlar
        CREATE TABLE IF NOT EXISTS promo_codes (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            code        TEXT    UNIQUE,
            days        INTEGER DEFAULT 30,
            max_uses    INTEGER DEFAULT -1,
            used_count  INTEGER DEFAULT 0,
            is_active   INTEGER DEFAULT 1,
            created_at  TEXT    DEFAULT (datetime('now'))
        );

        -- Promo kod ishlatilishi
        CREATE TABLE IF NOT EXISTS promo_uses (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            code_id     INTEGER,
            user_id     INTEGER,
            used_at     TEXT    DEFAULT (datetime('now'))
        );

        -- Bot sozlamalari (to'lov matni, help matni har til uchun)
        CREATE TABLE IF NOT EXISTS settings (
            key     TEXT PRIMARY KEY,
            value   TEXT DEFAULT '{}'
        );

        -- Rejalashtirilgan broadcast
        CREATE TABLE IF NOT EXISTS scheduled_bc (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            msg_data    TEXT,
            scheduled_at TEXT,
            status      TEXT DEFAULT 'pending',
            created_by  INTEGER,
            created_at  TEXT DEFAULT (datetime('now'))
        );

        -- Ban jurnali
        CREATE TABLE IF NOT EXISTS ban_log (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER,
            admin_id    INTEGER,
            reason      TEXT    DEFAULT '',
            action      TEXT    DEFAULT 'ban',
            done_at     TEXT    DEFAULT (datetime('now'))
        );
        """)

    # Default sozlamalarni o'rnatish
    _init_default_settings()


def _db():
    return sqlite3.connect(DB_PATH)


def _init_default_settings():
    defaults = {
        "payment_text": json.dumps({
            "uz": (
                "💳 *To'lov ma'lumotlari:*\n\n"
                "🔵 Click: `+998901234567`\n"
                "🟢 Payme: `+998901234567`\n"
                "💳 Uzcard: `8600 0000 0000 0000`\n"
                "👤 Karta egasi: Ism Familiya\n\n"
                "💰 Narx: $3 / 1 oy\n\n"
                "To'lov qilgandan so'ng screenshotni yuboring."
            ),
            "ru": (
                "💳 *Реквизиты для оплаты:*\n\n"
                "🔵 Click: `+998901234567`\n"
                "🟢 Payme: `+998901234567`\n"
                "💳 Uzcard: `8600 0000 0000 0000`\n"
                "👤 Владелец: Имя Фамилия\n\n"
                "💰 Цена: $3 / 1 месяц\n\n"
                "После оплаты отправьте скриншот."
            ),
            "en": (
                "💳 *Payment details:*\n\n"
                "🔵 Click: `+998901234567`\n"
                "🟢 Payme: `+998901234567`\n"
                "💳 Uzcard: `8600 0000 0000 0000`\n"
                "👤 Name: First Last\n\n"
                "💰 Price: $3 / month\n\n"
                "Send screenshot after payment."
            ),
        }),
        "help_text": json.dumps({
            "uz": (
                "❓ *Yordam*\n\n"
                "🎬 Video yuboring → ovoz + MP3\n"
                "🎤 Ovozli xabar → MP3 + kesish\n"
                "🎵 MP3 → ovoz + kesish\n"
                "🔗 YouTube/Instagram → video + ovoz\n\n"
                "⭐ *Premium imkoniyatlar:*\n"
                "✂️ Istalgan vaqtdan kesish\n"
                "🔄 Tezlik o'zgartirish\n"
                "🎙 Vocal ajratish\n"
                "🔇 Shovqin yo'qotish\n"
                "📥 1080p gacha video yuklab olish\n\n"
                "Muammo bo'lsa admin bilan bog'laning."
            ),
            "ru": (
                "❓ *Помощь*\n\n"
                "🎬 Видео → звук + MP3\n"
                "🎤 Голосовое → MP3 + обрезка\n"
                "🎵 MP3 → голосовое + обрезка\n"
                "🔗 YouTube/Instagram → видео + звук\n\n"
                "⭐ *Премиум возможности:*\n"
                "✂️ Обрезка в любом месте\n"
                "🔄 Изменение скорости\n"
                "🎙 Выделение вокала\n"
                "🔇 Шумоподавление\n"
                "📥 Скачивание до 1080p\n\n"
                "Проблемы? Обратитесь к администратору."
            ),
            "en": (
                "❓ *Help*\n\n"
                "🎬 Video → audio + MP3\n"
                "🎤 Voice message → MP3 + trim\n"
                "🎵 MP3 → voice + trim\n"
                "🔗 YouTube/Instagram → video + audio\n\n"
                "⭐ *Premium features:*\n"
                "✂️ Trim at any point\n"
                "🔄 Speed adjustment\n"
                "🎙 Vocal isolation\n"
                "🔇 Noise removal\n"
                "📥 Download up to 1080p\n\n"
                "Issues? Contact the admin."
            ),
        }),
    }
    with _db() as c:
        for key, val in defaults.items():
            c.execute(
                "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)",
                (key, val),
            )


# ════════════════════════════════════════════════════════
#  FOYDALANUVCHILAR
# ════════════════════════════════════════════════════════
def ensure_user(uid: int, username: str, first_name: str, tg_lang: str = ""):
    with _db() as c:
        c.execute("""
            INSERT INTO users (user_id, username, first_name, tg_language)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                username      = excluded.username,
                first_name    = excluded.first_name,
                tg_language   = excluded.tg_language,
                last_activity = datetime('now')
        """, (uid, username or "", first_name or "", tg_lang or ""))


def get_user(uid: int):
    with _db() as c:
        return c.execute("SELECT * FROM users WHERE user_id=?", (uid,)).fetchone()


def get_lang(uid: int) -> str:
    with _db() as c:
        row = c.execute(
            "SELECT bot_language FROM users WHERE user_id=?", (uid,)
        ).fetchone()
    return row[0] if row else "en"


def set_lang(uid: int, lang: str):
    with _db() as c:
        c.execute("UPDATE users SET bot_language=? WHERE user_id=?", (lang, uid))


def is_banned(uid: int) -> bool:
    with _db() as c:
        row = c.execute(
            "SELECT is_banned FROM users WHERE user_id=?", (uid,)
        ).fetchone()
    return bool(row and row[0])


def ban_user(uid: int, admin_id: int, reason: str = ""):
    with _db() as c:
        c.execute(
            "UPDATE users SET is_banned=1, ban_reason=? WHERE user_id=?",
            (reason, uid),
        )
        c.execute(
            "INSERT INTO ban_log (user_id, admin_id, reason, action) VALUES (?,?,?,'ban')",
            (uid, admin_id, reason),
        )


def unban_user(uid: int, admin_id: int):
    with _db() as c:
        c.execute(
            "UPDATE users SET is_banned=0, ban_reason='' WHERE user_id=?", (uid,)
        )
        c.execute(
            "INSERT INTO ban_log (user_id, admin_id, action) VALUES (?,?,'unban')",
            (uid, admin_id),
        )


def get_banned_users(limit: int = 50) -> list:
    with _db() as c:
        return c.execute("""
            SELECT user_id, first_name, username, ban_reason
            FROM users WHERE is_banned=1
            ORDER BY created_at DESC LIMIT ?
        """, (limit,)).fetchall()


def bump_activity(uid: int):
    with _db() as c:
        c.execute(
            "UPDATE users SET last_activity=datetime('now') WHERE user_id=?", (uid,)
        )


# ════════════════════════════════════════════════════════
#  PREMIUM
# ════════════════════════════════════════════════════════
def is_premium(uid: int) -> bool:
    with _db() as c:
        row = c.execute(
            "SELECT is_premium, premium_until FROM users WHERE user_id=?", (uid,)
        ).fetchone()
    if not row or not row[0] or not row[1]:
        return False
    try:
        return datetime.fromisoformat(row[1]) > datetime.now()
    except ValueError:
        return False


def premium_until(uid: int):
    with _db() as c:
        row = c.execute(
            "SELECT premium_until FROM users WHERE user_id=?", (uid,)
        ).fetchone()
    if not row or not row[0]:
        return None
    try:
        return datetime.fromisoformat(row[0])
    except ValueError:
        return None


def grant_premium(uid: int, days: int = None) -> datetime:
    if days is None:
        days = PREMIUM_DAYS
    cur   = premium_until(uid)
    base  = cur if (cur and cur > datetime.now()) else datetime.now()
    until = base + timedelta(days=days)
    with _db() as c:
        c.execute("""
            UPDATE users SET
                is_premium     = 1,
                premium_until  = ?,
                purchase_count = purchase_count + 1
            WHERE user_id = ?
        """, (until.isoformat(), uid))
    return until


def revoke_premium(uid: int):
    with _db() as c:
        c.execute(
            "UPDATE users SET is_premium=0, premium_until='' WHERE user_id=?", (uid,)
        )


def get_expiring_soon(days_before: int = 3) -> list:
    """Premium {days_before} kun ichida tugaydigan foydalanuvchilar."""
    now    = datetime.now()
    future = (now + timedelta(days=days_before)).isoformat()
    with _db() as c:
        return c.execute("""
            SELECT user_id, first_name, bot_language, premium_until
            FROM users
            WHERE is_premium=1 AND premium_until<=? AND premium_until>?
        """, (future, now.isoformat())).fetchall()


# ════════════════════════════════════════════════════════
#  KUNLIK LIMIT
# ════════════════════════════════════════════════════════
def check_limit(uid: int) -> bool:
    """True → foydalanish mumkin."""
    from config import FREE_DAILY_LIMIT
    today = datetime.now().date().isoformat()
    with _db() as c:
        row = c.execute(
            "SELECT free_used, last_use_date FROM users WHERE user_id=?", (uid,)
        ).fetchone()
    if not row:
        return True
    used, last = row
    if last != today:
        with _db() as c:
            c.execute(
                "UPDATE users SET free_used=0, last_use_date=? WHERE user_id=?",
                (today, uid),
            )
        return True
    return used < FREE_DAILY_LIMIT


def bump_usage(uid: int):
    today = datetime.now().date().isoformat()
    with _db() as c:
        c.execute("""
            UPDATE users SET
                free_used       = free_used + 1,
                last_use_date   = ?,
                total_processed = total_processed + 1,
                last_activity   = datetime('now')
            WHERE user_id = ?
        """, (today, uid))


def used_today(uid: int) -> int:
    today = datetime.now().date().isoformat()
    with _db() as c:
        row = c.execute(
            "SELECT free_used, last_use_date FROM users WHERE user_id=?", (uid,)
        ).fetchone()
    if not row:
        return 0
    return row[0] if row[1] == today else 0


# ════════════════════════════════════════════════════════
#  TO'LOV
# ════════════════════════════════════════════════════════
def add_payment_screenshot(uid: int, file_id: str) -> int:
    with _db() as c:
        cur = c.execute("""
            INSERT INTO payments (user_id, pay_type, screenshot_id)
            VALUES (?, 'screenshot', ?)
        """, (uid, file_id))
        return cur.lastrowid


def add_payment_stars(uid: int, charge_id: str, amount: int) -> int:
    with _db() as c:
        cur = c.execute("""
            INSERT INTO payments (user_id, pay_type, stars_charge_id, amount_stars, status)
            VALUES (?, 'stars', ?, ?, 'completed')
        """, (uid, charge_id, amount))
        return cur.lastrowid


def get_payment(pid: int):
    with _db() as c:
        return c.execute("SELECT * FROM payments WHERE id=?", (pid,)).fetchone()


def set_payment_status(pid: int, status: str):
    with _db() as c:
        c.execute("UPDATE payments SET status=? WHERE id=?", (status, pid))


def get_pending_payments(limit: int = 20) -> list:
    with _db() as c:
        return c.execute("""
            SELECT p.id, p.user_id, u.first_name, u.username,
                   p.screenshot_id, p.created_at
            FROM payments p
            LEFT JOIN users u ON p.user_id=u.user_id
            WHERE p.status='pending' AND p.pay_type='screenshot'
            ORDER BY p.created_at DESC LIMIT ?
        """, (limit,)).fetchall()


# ════════════════════════════════════════════════════════
#  PROMO KODLAR
# ════════════════════════════════════════════════════════
def create_promo(code: str, days: int, max_uses: int = -1) -> bool:
    try:
        with _db() as c:
            c.execute("""
                INSERT INTO promo_codes (code, days, max_uses)
                VALUES (?, ?, ?)
            """, (code.upper(), days, max_uses))
        return True
    except sqlite3.IntegrityError:
        return False


def use_promo(uid: int, code: str) -> dict:
    """
    Qaytadi: {'ok': True, 'days': 30} yoki {'ok': False, 'reason': '...'}
    """
    code = code.upper().strip()
    with _db() as c:
        row = c.execute("""
            SELECT id, days, max_uses, used_count, is_active
            FROM promo_codes WHERE code=?
        """, (code,)).fetchone()

    if not row:
        return {"ok": False, "reason": "invalid"}
    pid, days, max_uses, used_count, is_active = row
    if not is_active:
        return {"ok": False, "reason": "invalid"}
    if max_uses != -1 and used_count >= max_uses:
        return {"ok": False, "reason": "invalid"}

    # Foydalanuvchi allaqachon ishlatganmi?
    with _db() as c:
        existing = c.execute(
            "SELECT id FROM promo_uses WHERE code_id=? AND user_id=?",
            (pid, uid),
        ).fetchone()
    if existing:
        return {"ok": False, "reason": "used"}

    # Ishlatish
    with _db() as c:
        c.execute(
            "INSERT INTO promo_uses (code_id, user_id) VALUES (?,?)", (pid, uid)
        )
        c.execute(
            "UPDATE promo_codes SET used_count=used_count+1 WHERE id=?", (pid,)
        )
    return {"ok": True, "days": days}


def get_promo_list(active_only: bool = False) -> list:
    with _db() as c:
        if active_only:
            return c.execute("""
                SELECT code, days, max_uses, used_count, is_active, created_at
                FROM promo_codes WHERE is_active=1
                ORDER BY created_at DESC
            """).fetchall()
        return c.execute("""
            SELECT code, days, max_uses, used_count, is_active, created_at
            FROM promo_codes ORDER BY created_at DESC LIMIT 30
        """).fetchall()


def toggle_promo(code: str, active: int):
    with _db() as c:
        c.execute(
            "UPDATE promo_codes SET is_active=? WHERE code=?",
            (active, code.upper()),
        )


# ════════════════════════════════════════════════════════
#  SOZLAMALAR (to'lov matni, help matni)
# ════════════════════════════════════════════════════════
def get_setting(key: str) -> dict:
    """JSON dict qaytaradi."""
    with _db() as c:
        row = c.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    if not row:
        return {}
    try:
        return json.loads(row[0])
    except (json.JSONDecodeError, TypeError):
        return {}


def set_setting(key: str, lang: str, value: str):
    """Bitta til uchun qiymat o'zgartirish."""
    data = get_setting(key)
    data[lang] = value
    with _db() as c:
        c.execute(
            "INSERT OR REPLACE INTO settings (key, value) VALUES (?,?)",
            (key, json.dumps(data, ensure_ascii=False)),
        )


def get_payment_text(lang: str) -> str:
    data = get_setting("payment_text")
    return data.get(lang, data.get("en", ""))


def get_help_text(lang: str) -> str:
    data = get_setting("help_text")
    return data.get(lang, data.get("en", ""))


# ════════════════════════════════════════════════════════
#  REFERAL
# ════════════════════════════════════════════════════════
def ref_count(uid: int) -> int:
    with _db() as c:
        return c.execute(
            "SELECT COUNT(*) FROM users WHERE referred_by=?", (uid,)
        ).fetchone()[0]


def add_bonus_days(uid: int, days: int):
    with _db() as c:
        c.execute(
            "UPDATE users SET bonus_days=bonus_days+? WHERE user_id=?", (days, uid)
        )
    # Agar premium bo'lsa, muddatiga qo'shish
    if is_premium(uid):
        until = premium_until(uid) + timedelta(days=days)
        with _db() as c:
            c.execute(
                "UPDATE users SET premium_until=? WHERE user_id=?",
                (until.isoformat(), uid),
            )


def set_referred_by(uid: int, ref_id: int) -> bool:
    """True = referral yangi (avval yo'q edi)."""
    row = get_user(uid)
    if not row or row[11] != 0:  # referred_by column
        return False
    with _db() as c:
        c.execute("UPDATE users SET referred_by=? WHERE user_id=?", (ref_id, uid))
    return True


# ════════════════════════════════════════════════════════
#  STATISTIKA
# ════════════════════════════════════════════════════════
def get_stats() -> dict:
    now   = datetime.now()
    week  = (now - timedelta(days=7)).isoformat()
    month = (now - timedelta(days=30)).isoformat()
    today = now.date().isoformat()
    with _db() as c:
        total    = c.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        active   = c.execute("SELECT COUNT(*) FROM users WHERE last_activity>=?", (week,)).fetchone()[0]
        prem_cnt = c.execute(
            "SELECT COUNT(*) FROM users WHERE is_premium=1 AND premium_until>?",
            (now.isoformat(),),
        ).fetchone()[0]
        banned   = c.execute("SELECT COUNT(*) FROM users WHERE is_banned=1").fetchone()[0]
        n_today  = c.execute("SELECT COUNT(*) FROM users WHERE date(created_at)=?", (today,)).fetchone()[0]
        n_week   = c.execute("SELECT COUNT(*) FROM users WHERE created_at>=?", (week,)).fetchone()[0]
        n_month  = c.execute("SELECT COUNT(*) FROM users WHERE created_at>=?", (month,)).fetchone()[0]
        pending  = c.execute("SELECT COUNT(*) FROM payments WHERE status='pending'").fetchone()[0]

    return dict(
        total=total, active=active, inactive=total - active - banned,
        premium=prem_cnt, banned=banned,
        new_today=n_today, new_week=n_week, new_month=n_month,
        pending_pays=pending,
    )


def get_country_stats() -> list:
    """language_code bo'yicha foydalanuvchilar soni."""
    with _db() as c:
        return c.execute("""
            SELECT
                CASE WHEN tg_language='' THEN 'unknown' ELSE tg_language END as lang,
                COUNT(*) as cnt
            FROM users
            GROUP BY lang
            ORDER BY cnt DESC
            LIMIT 25
        """).fetchall()


def get_premium_recent(limit: int = 30) -> list:
    with _db() as c:
        return c.execute("""
            SELECT user_id, first_name, username, purchase_count, premium_until
            FROM users WHERE purchase_count>0
            ORDER BY premium_until DESC LIMIT ?
        """, (limit,)).fetchall()


def get_premium_top(limit: int = 30) -> list:
    with _db() as c:
        return c.execute("""
            SELECT user_id, first_name, username, purchase_count, premium_until
            FROM users WHERE purchase_count>0
            ORDER BY purchase_count DESC LIMIT ?
        """, (limit,)).fetchall()


# ════════════════════════════════════════════════════════
#  BROADCAST
# ════════════════════════════════════════════════════════
def all_user_ids(exclude_banned: bool = True) -> list:
    with _db() as c:
        if exclude_banned:
            return [r[0] for r in c.execute(
                "SELECT user_id FROM users WHERE is_banned=0"
            ).fetchall()]
        return [r[0] for r in c.execute("SELECT user_id FROM users").fetchall()]


def save_scheduled_bc(msg_data: dict, scheduled_at: str, admin_id: int) -> int:
    with _db() as c:
        cur = c.execute("""
            INSERT INTO scheduled_bc (msg_data, scheduled_at, created_by)
            VALUES (?, ?, ?)
        """, (json.dumps(msg_data, ensure_ascii=False), scheduled_at, admin_id))
        return cur.lastrowid


def get_pending_scheduled() -> list:
    now = datetime.now().isoformat()
    with _db() as c:
        return c.execute("""
            SELECT id, msg_data, scheduled_at, created_by
            FROM scheduled_bc
            WHERE status='pending' AND scheduled_at<=?
            ORDER BY scheduled_at ASC
        """, (now,)).fetchall()


def mark_scheduled_sent(bc_id: int):
    with _db() as c:
        c.execute(
            "UPDATE scheduled_bc SET status='sent' WHERE id=?", (bc_id,)
        )


def get_scheduled_list() -> list:
    with _db() as c:
        return c.execute("""
            SELECT id, scheduled_at, status, created_at
            FROM scheduled_bc
            WHERE status='pending'
            ORDER BY scheduled_at ASC LIMIT 10
        """).fetchall()


def cancel_scheduled(bc_id: int):
    with _db() as c:
        c.execute(
            "UPDATE scheduled_bc SET status='cancelled' WHERE id=?", (bc_id,)
        )
