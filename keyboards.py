Copy

"""
⌨️ VTVS Bot — Klaviaturalar
Foydalanuvchi: faqat InlineKeyboard
Admin: faqat ReplyKeyboard
"""
from telegram import (
    InlineKeyboardButton as IKB,
    InlineKeyboardMarkup as IKM,
    KeyboardButton as KB,
    ReplyKeyboardMarkup as RKM,
)
from translations import tx
 
 
# ════════════════════════════════════════════════════════
#  ADMIN REPLY KEYBOARD
# ════════════════════════════════════════════════════════
ADMIN_KB = RKM([
    [KB("📊 Statistika"),         KB("🌍 Davlatlar")],
    [KB("📢 Xabar yuborish"),     KB("📅 Rejalashtirilgan")],
    [KB("👑 Yaqinda premium"),    KB("🏆 Ko'p sotib olgan")],
    [KB("✅ Premium berish"),     KB("❌ Premium olish")],
    [KB("🚫 Ban"),                KB("✅ Unban")],
    [KB("📋 Banlanganlar"),       KB("📋 Kutayotgan to'lovlar")],
    [KB("💳 To'lov matni"),       KB("❓ Help matni")],
    [KB("🎟 Promo kodlar"),       KB("➕ Promo yaratish")],
], resize_keyboard=True)
 
# Broadcast turi tanlash
BC_TYPE_KB = RKM([
    [KB("✍️ Oddiy xabar"),         KB("↩️ Forward rejim")],
    [KB("🖼 Ko'p mediali reklama"), KB("📅 Rejalashtirilgan")],
    [KB("◀️ Orqaga")],
], resize_keyboard=True)
 
# Ko'p media yig'ish
MEDIA_COLLECT_KB = RKM([
    [KB("✅ Reklama tayyor"), KB("❌ Bekor")],
], resize_keyboard=True)
 
# Tasdiqlash
CONFIRM_KB = RKM([
    [KB("✅ Ha, yubor"), KB("❌ Bekor")],
], resize_keyboard=True)
 
# Caption
CAPTION_KB = RKM([
    [KB("⏭ Caption yo'q"), KB("❌ Bekor")],
], resize_keyboard=True)
 
# Til sozlamasi (admin uchun)
LANG_EDIT_KB = RKM([
    [KB("🇺🇿 O'zbek matni"),  KB("🇷🇺 Rus matni")],
    [KB("🇬🇧 Ingliz matni"),  KB("◀️ Orqaga")],
], resize_keyboard=True)
 
# Bekor tugmasi
CANCEL_KB = RKM([[KB("❌ Bekor")]], resize_keyboard=True)
 
 
# ════════════════════════════════════════════════════════
#  FOYDALANUVCHI INLINE KEYBOARD
# ════════════════════════════════════════════════════════
def lang_kb() -> IKM:
    """Til tanlash."""
    return IKM([[
        IKB("🇺🇿 O'zbek", callback_data="lang:uz"),
        IKB("🇷🇺 Русский",  callback_data="lang:ru"),
        IKB("🇬🇧 English",  callback_data="lang:en"),
    ]])
 
 
def main_menu_kb(lang: str) -> IKM:
    """Asosiy menyu."""
    return IKM([
        [
            IKB(tx(lang, "get_premium"),  callback_data="menu:premium"),
            IKB(tx(lang, "ref_btn"),      callback_data="menu:ref"),
        ],
        [
            IKB(tx(lang, "my_status_btn"), callback_data="menu:status"),
            IKB(tx(lang, "change_lang"),   callback_data="menu:lang"),
        ],
    ])
 
 
 
def premium_kb(lang: str) -> IKM:
    """To'lov tugmalari."""
    return IKM([
        [IKB(tx(lang, "pay_stars"),  callback_data="pay:stars")],
        [IKB(tx(lang, "i_paid"),     callback_data="pay:screenshot")],
        [IKB(tx(lang, "promo_btn"),  callback_data="pay:promo")],
    ])
 
 
def renew_kb(lang: str) -> IKM:
    """Premium yangilash (tugash ogohlantiruvi uchun)."""
    return IKM([[IKB(tx(lang, "get_premium"), callback_data="menu:premium")]])
 
 
def action_kb(lang: str, is_premium: bool) -> IKM:
    """Video/audio qayta ishlash tanlash."""
    rows = [[IKB(tx(lang, "full_extract"), callback_data="action:full")]]
    if is_premium:
        rows += [
            [IKB(tx(lang, "trim_btn"),  callback_data="action:trim"),
             IKB(tx(lang, "speed_btn"), callback_data="action:speed")],
            [IKB(tx(lang, "vocal_btn"), callback_data="action:vocal"),
             IKB(tx(lang, "noise_btn"), callback_data="action:noise")],
        ]
    else:
        rows += [[IKB(tx(lang, "trim_btn"),  callback_data="action:trim")]]
        rows += [[IKB("⭐ Premium — ko'proq imkoniyat", callback_data="menu:premium")]]
    return IKM(rows)
 
 
def speed_kb(lang: str) -> IKM:
    """Tezlik tanlash."""
    return IKM([
        [IKB(tx(lang, "speed_05"),  callback_data="speed:0.5"),
         IKB(tx(lang, "speed_075"), callback_data="speed:0.75")],
        [IKB(tx(lang, "speed_10"),  callback_data="speed:1.0"),
         IKB(tx(lang, "speed_125"), callback_data="speed:1.25")],
        [IKB(tx(lang, "speed_15"),  callback_data="speed:1.5"),
         IKB(tx(lang, "speed_20"),  callback_data="speed:2.0")],
        [IKB(tx(lang, "back"),      callback_data="action:back")],
    ])
 
 
def quality_kb(lang: str, is_premium: bool) -> IKM:
    """YouTube/Instagram sifat tanlash."""
    if is_premium:
        return IKM([
            [IKB(tx(lang, "q_360"),   callback_data="yt:360"),
             IKB(tx(lang, "q_480"),   callback_data="yt:480")],
            [IKB(tx(lang, "q_720"),   callback_data="yt:720"),
             IKB(tx(lang, "q_1080"),  callback_data="yt:1080")],
            [IKB(tx(lang, "q_audio"), callback_data="yt:audio")],
        ])
    return IKM([
        [IKB(tx(lang, "q_360"),   callback_data="yt:360")],
        [IKB(tx(lang, "q_audio"), callback_data="yt:audio")],
        [IKB("⭐ Premium — barcha sifatlar", callback_data="menu:premium")],
    ])
 
 
def admin_pay_kb(pay_id: int) -> IKM:
    """Admin uchun to'lov tasdiqlash tugmalari."""
    return IKM([[
        IKB("✅ Tasdiqlash", callback_data=f"admpay:approve:{pay_id}"),
        IKB("❌ Rad etish",  callback_data=f"admpay:reject:{pay_id}"),
    ]])
