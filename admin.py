"""
👑 VTVS Bot — Admin panel handlerlari
"""
import json
import logging
from datetime import datetime

from telegram import Update
from telegram.ext import ContextTypes

from config import ADMINIDS, PREMIUMDAYS
from database import (
    getstats, getcountry_stats,
    getpremiumrecent, getpremiumtop,
    grantpremium, revokepremium,
    banuser, unbanuser, getbannedusers,
    getpendingpayments, setpaymentstatus, get_payment,
    getsetting, setsetting,
    createpromo, getpromolist, togglepromo,
    savescheduledbc, getscheduledlist, cancel_scheduled,
    alluserids,
)
from broadcast import broadcastsingle, broadcastalbum, msgtodict, done_text
from keyboards import (
    ADMINKB, BCTYPEKB, MEDIACOLLECTKB, CONFIRMKB,
    CAPTIONKB, LANGEDITKB, CANCELKB,
    adminpaykb,
)

logger = logging.getLogger(_name_)

# Admin keyboard barcha tugmalari - state bilan konflikt bo'lmasin
ADMINMENUBTNS = {
    "📊 Statistika", "🌍 Davlatlar", "📢 Xabar yuborish",
    "📅 Rejalashtirilgan", "👑 Yaqinda premium", "🏆 Ko'p sotib olgan",
    "✅ Premium berish", "❌ Premium olish", "🚫 Ban", "✅ Unban",
    "📋 Banlanganlar", "📋 Kutayotgan to'lovlar", "💳 To'lov matni",
    "❓ Help matni", "🎟 Promo kodlar", "➕ Promo yaratish",
    "✍️ Oddiy xabar", "↩️ Forward rejim", "🖼 Ko'p mediali reklama",
    "◀️ Orqaga", "❌ Bekor", "✅ Ha, yubor", "⏭ Caption yo'q",
    "🇺🇿 O'zbek matni", "🇷🇺 Rus matni", "🇬🇧 Ingliz matni",
}


# language_code → bayroq
FLAG = {
    "uz": "🇺🇿", "ru": "🇷🇺", "en": "🇬🇧", "tr": "🇹🇷",
    "fa": "🇮🇷", "ar": "🇸🇦", "id": "🇮🇩", "de": "🇩🇪",
    "fr": "🇫🇷", "es": "🇪🇸", "pt": "🇧🇷", "zh-hans": "🇨🇳",
    "zh-hant": "🇹🇼", "ja": "🇯🇵", "ko": "🇰🇷", "uk": "🇺🇦",
    "kk": "🇰🇿", "ky": "🇰🇬", "tg": "🇹🇯", "tk": "🇹🇲",
    "az": "🇦🇿", "he": "🇮🇱", "hi": "🇮🇳", "unknown": "🌍",
}


async def send_long(msg, text: str, kb, chunk: int = 4000):
    """Uzun xabarni bo'lib yuborish."""
    parts = [text[i:i + chunk] for i in range(0, len(text), chunk)]
    for i, p in enumerate(parts):
        await msg.reply_text(
            p,
            reply_markup=kb if i == len(parts) - 1 else None,
        )


# ════════════════════════════════════════════════════════
#  ADMIN MEDIA HANDLER
# ════════════════════════════════════════════════════════
async def onmedia(update: Update, context: ContextTypes.DEFAULTTYPE):
    """Admin rasm/video yuborganda."""
    msg = update.message
    ud  = context.user_data
    st  = ud.get("st")

    if st == "bcmediacollect":
        items = ud.setdefault("bc_items", [])
        from config import MAX_ALBUM
        if len(items) >= MAX_ALBUM:
            await msg.reply_text(
                f"⚠️ Maksimal {MAX_ALBUM} ta. '✅ Reklama tayyor' bosing.",
                replymarkup=MEDIACOLLECT_KB,
            )
            return

        if msg.photo:
            items.append({"type": "photo", "fileid": msg.photo[-1].fileid})
            icon = "📸"
        elif msg.video:
            items.append({"type": "video", "fileid": msg.video.fileid})
            icon = "🎬"
        else:
            await msg.replytext("⚠️ Faqat 📸 yoki 🎬 yuboring.", replymarkup=MEDIACOLLECTKB)
            return

        n = len(items)
        await msg.reply_text(
            f"{icon} {n}/10 qo'shildi.\n" +
            ("Yana qo'shing yoki 'Tayyor' bosing." if n < MAX_ALBUM
             else "Limit to'ldi. '✅ Tayyor' bosing."),
            replymarkup=MEDIACOLLECT_KB,
        )
        return

    if st in ("bcsingle", "bcforward"):
        src = msgtodict(msg)
        uids = alluserids()
        ud["st"]  = f"{st}_confirm"
        ud["src"] = src
        await msg.reply_text(
            f"📢 Tasdiqlang:\n\n"
            f"📌 Tur: {src['type']}\n"
            f"👥 Yuboriladi: {len(uids)} ta",
            replymarkup=CONFIRMKB,
        )


# ════════════════════════════════════════════════════════
#  ADMIN TEXT HANDLER
# ════════════════════════════════════════════════════════
async def ontext(update: Update, context: ContextTypes.DEFAULTTYPE):
    text = update.message.text or ""
    ud   = context.user_data
    bot  = context.bot
    st   = ud.get("st")

    # ── Universal bekor qilish ────────────────────────
    if text == "❌ Bekor":
        ud.clear()
        await update.message.replytext("❌ Bekor qilindi.", replymarkup=ADMIN_KB)
        return

    # ════════════════════════════════════════════════
    #  BROADCAST STATE MACHINE
    # ════════════════════════════════════════════════

    if st == "bcmediacollect" and text == "✅ Reklama tayyor":
        items = ud.get("bc_items", [])
        if not items:
            await update.message.replytext("⚠️ Hali hech narsa yo'q.", replymarkup=MEDIACOLLECTKB)
            return
        ud["st"] = "bc_caption"
        await update.message.reply_text(
            f"✅ {len(items)} ta media qo'shildi!\n\n"
            "📝 Matn (caption) yuboring yoki '⏭ Caption yo'q' bosing.",
            replymarkup=CAPTIONKB,
        )
        return

    if st == "bc_caption":
        caption = "" if text == "⏭ Caption yo'q" else text
        items   = ud.get("bc_items", [])
        uids    = alluserids()
        ud["st"]         = "bcalbumconfirm"
        ud["bc_caption"] = caption
        p = sum(1 for x in items if x["type"] == "photo")
        v = sum(1 for x in items if x["type"] == "video")
        cap_prev = (caption[:60] + "...") if len(caption) > 60 else caption
        await update.message.reply_text(
            f"🖼 Tasdiqlang:\n\n"
            f"📸 {p} rasm | 🎬 {v} video\n"
            f"📝 {cap_prev or "Yoq"}\n"
            f"👥 {len(uids)} ta foydalanuvchi\n\nYuborilsinmi?",
            replymarkup=CONFIRMKB,
        )
        return

    if st in ("bcsingle", "bcforward") and text not in ("✅ Ha, yubor",):
        # Matnli xabar
        src  = msgtodict(update.message)
        uids = alluserids()
        ud["st"]  = f"{st}_confirm"
        ud["src"] = src
        prev = (text[:80] + "...") if len(text) > 80 else text
        await update.message.reply_text(
            f"✍️ Tasdiqlang:\n\n{prev}\n\n👥 {len(uids)} ta",
            replymarkup=CONFIRMKB,
        )
        return

    # ── HA, YUBOR ────────────────────────────────────
    if text == "✅ Ha, yubor":
        if st == "bcsingleconfirm":
            src  = ud.pop("src", {})
            ud.clear()
            uids = alluserids()
            prog = await update.message.reply_text(
                f"📢 Yuborilmoqda... 0/{len(uids)}", replymarkup=ADMINKB
            )
            ok, fail = await broadcast_single(bot, src, uids, prog)
            await prog.edit_text(
                done_text("Xabar yuborildi!", ok, fail, len(uids)),
            )
            return

        if st == "bcforwardconfirm":
            src  = ud.pop("src", {})
            ud.clear()
            uids = alluserids()
            prog = await update.message.reply_text(
                f"↩️ Forward qilinmoqda... 0/{len(uids)}", replymarkup=ADMINKB
            )
            ok, fail = await broadcast_single(bot, src, uids, prog)
            await prog.edit_text(
                done_text("Forward yuborildi!", ok, fail, len(uids)),
            )
            return

        if st == "bcalbumconfirm":
            items   = ud.pop("bc_items", [])
            caption = ud.pop("bc_caption", "")
            ud.clear()
            uids = alluserids()
            prog = await update.message.reply_text(
                f"🖼 Reklama yuborilmoqda... 0/{len(uids)}", replymarkup=ADMINKB
            )
            ok, fail = await broadcast_album(bot, items, caption, uids, prog)
            await prog.edit_text(
                done_text("Reklama yuborildi!", ok, fail, len(uids),
                          extra=f"🖼 Media: {len(items)} ta"),
            )
            return

        if st == "bcscheduledconfirm":
            src  = ud.pop("src", {})
            sdt  = ud.pop("sched_dt", "")
            uid  = update.effective_user.id
            ud.clear()
            bcid = savescheduled_bc(src, sdt, uid)
            await update.message.reply_text(
                f"✅ Rejalashtirildi!\n📅 {sdt[:16]}\n🆔 #{bc_id}",
                replymarkup=ADMINKB,
            )
            return

    # ════════════════════════════════════════════════
    #  TO'LOV MATNI TAHRIRLASH
    # ════════════════════════════════════════════════
    if st in ("editpayuz", "editpayru", "editpayen"):
        langmap = {"editpayuz": "uz", "editpayru": "ru", "editpay_en": "en"}
        lang = lang_map[st]
        setsetting("paymenttext", lang, text)
        ud.clear()
        await update.message.reply_text(
            f"✅ To'lov matni saqlandi! ({lang.upper()})", replymarkup=ADMINKB
        )
        return

    if st in ("edithelpuz", "edithelpru", "edithelpen"):
        langmap = {"edithelpuz": "uz", "edithelpru": "ru", "edithelp_en": "en"}
        lang = lang_map[st]
        setsetting("helptext", lang, text)
        ud.clear()
        await update.message.reply_text(
            f"✅ Help matni saqlandi! ({lang.upper()})", replymarkup=ADMINKB
        )
        return

    # ════════════════════════════════════════════════
    #  PROMO KOD YARATISH
    # ════════════════════════════════════════════════
    if st == "promo_create" and text not in (
        "📊 Statistika", "🌍 Davlatlar", "📢 Xabar yuborish",
        "📅 Rejalashtirilgan", "👑 Yaqinda premium", "🏆 Ko'p sotib olgan",
        "✅ Premium berish", "❌ Premium olish", "🚫 Ban", "✅ Unban",
        "📋 Banlanganlar", "📋 Kutayotgan to'lovlar", "💳 To'lov matni",
        "❓ Help matni", "🎟 Promo kodlar", "➕ Promo yaratish",
        "✍️ Oddiy xabar", "↩️ Forward rejim", "🖼 Ko'p mediali reklama",
        "◀️ Orqaga", "❌ Bekor",
    ):
        # Format: KOD 30 100  (kod, kun, max_uses)
        parts = text.strip().split()
        try:
            code = parts[0].upper()
            days = int(parts[1]) if len(parts) > 1 else PREMIUM_DAYS
            max_u = int(parts[2]) if len(parts) > 2 else -1
            ok = createpromo(code, days, maxu)
            ud.clear()
            if ok:
                await update.message.reply_text(
                    f"✅ Promo kod yaratildi!\n"
                    f"🎟 Kod: {code}\n"
                    f"📅 Kunlar: {days}\n"
                    f"Max: {'Cheksiz' if maxu == -1 else maxu}",
                    replymarkup=ADMINKB,
                )
            else:
                await update.message.reply_text(
                    "❌ Bu kod allaqachon mavjud.", replymarkup=ADMINKB
                )
        except (IndexError, ValueError):
            await update.message.reply_text(
                "❌ Format: KOD 30 100\nkod kun maxuses_",
            )
        return

    # ════════════════════════════════════════════════
    #  REJALASHTIRILGAN BROADCAST
    # ════════════════════════════════════════════════
    if st == "bcscheduledmsg":
        src = msgtodict(update.message)
        ud["st"]  = "bcscheduleddt"
        ud["src"] = src
        await update.message.reply_text(
            "📅 Yuborish vaqtini kiriting:\n"
            "Format: DD.MM.YYYY HH:MM\n"
            "Misol: 25.12.2025 10:00",
        )
        return

    if st == "bcscheduleddt":
        try:
            dt = datetime.strptime(text.strip(), "%d.%m.%Y %H:%M")
            if dt <= datetime.now():
                await update.message.reply_text("❌ Vaqt o'tib ketgan. Kelajak vaqt kiriting.")
                return
            ud["sched_dt"] = dt.isoformat()
            ud["st"]       = "bcscheduledconfirm"
            uids = alluserids()
            await update.message.reply_text(
                f"📅 Tasdiqlang:\n\n"
                f"🕐 Vaqt: {text.strip()}\n"
                f"👥 {len(uids)} ta foydalanuvchi\n\nYuborilsinmi?",
                replymarkup=CONFIRMKB,
            )
        except ValueError:
            await update.message.reply_text(
                "❌ Format noto'g'ri. Misol: 25.12.2025 10:00",
            )
        return

    # ════════════════════════════════════════════════
    #  BAN / UNBAN
    # ════════════════════════════════════════════════
    if st == "banid" and text not in ADMINMENU_BTNS:
        try:
            parts = text.strip().split(None, 1)
            tid    = int(parts[0])
            reason = parts[1] if len(parts) > 1 else ""
            banuser(tid, update.effectiveuser.id, reason)
            ud.clear()
            await update.message.reply_text(
                f"🚫 Foydalanuvchi ban qilindi.\n🆔 {tid}", replymarkup=ADMINKB,
            )
            try:
                await bot.send_message(tid, "🚫 Siz botdan ban qilindingiz.")
            except Exception:
                pass
        except (ValueError, IndexError):
            await update.message.reply_text("❌ Format: ID [sabab]")
        return

    if st == "unbanid" and text not in ADMINMENU_BTNS:
        try:
            tid = int(text.strip())
            unbanuser(tid, update.effectiveuser.id)
            ud.clear()
            await update.message.reply_text(
                f"✅ Foydalanuvchi unban qilindi.\n🆔 {tid}", replymarkup=ADMINKB,
            )
            try:
                await bot.send_message(tid, "✅ Sizning baningiz olib tashlandi.")
            except Exception:
                pass
        except ValueError:
            await update.message.reply_text("❌ Faqat ID kiriting.")
        return

    # ════════════════════════════════════════════════
    #  PREMIUM BERISH / OLISH
    # ════════════════════════════════════════════════
    if st == "grantid" and text not in ADMINMENU_BTNS:
        try:
            parts = text.strip().split()
            tid   = int(parts[0])
            days  = int(parts[1]) if len(parts) > 1 else PREMIUM_DAYS
            until = grant_premium(tid, days)
            ud.clear()
            await update.message.reply_text(
                f"✅ Premium berildi!\n🆔 {tid}\n"
                f"📅 {until.strftime('%d.%m.%Y')} gacha", replymarkup=ADMINKB,
            )
            from database import get_lang
            tl = get_lang(tid)
            from translations import tx
            try:
                await bot.send_message(
                    tid,
                    tx(tl, "pay_confirmed", days=days, until=until.strftime("%d.%m.%Y")),
                )
            except Exception:
                pass
        except (ValueError, IndexError):
            await update.message.reply_text("❌ Format: ID [kunlar]")
        return

    if st == "revokeid" and text not in ADMINMENU_BTNS:
        try:
            tid = int(text.strip())
            revoke_premium(tid)
            ud.clear()
            await update.message.reply_text(
                f"✅ Premium bekor qilindi.\n🆔 {tid}", replymarkup=ADMINKB,
            )
        except ValueError:
            await update.message.reply_text("❌ Faqat ID kiriting.")
        return

    # ════════════════════════════════════════════════
    #  ASOSIY MENYUSI
    # ════════════════════════════════════════════════

    if text == "📊 Statistika":
        s = get_stats()
        await update.message.reply_text(
            f"📊 BOT STATISTIKASI\n{'━'*26}\n"
            f"👥 Jami: {s['total']}\n"
            f"🟢 Aktiv (7 kun): {s['active']}\n"
            f"🔴 Nofaol: {s['inactive']}\n"
            f"⭐ Premium: {s['premium']}\n"
            f"🚫 Banned: {s['banned']}\n"
            f"{"="*26}\n"
            f"📅 Bugun yangi: +{s['new_today']}\n"
            f"📅 Hafta: +{s['new_week']}\n"
            f"📅 Oy: +{s['new_month']}\n"
            f"{"="*26}\n"
            f"💳 Kutayotgan to'lovlar: {s['pendingpays']}", replymarkup=ADMIN_KB,
        )

    elif text == "🌍 Davlatlar":
        rows = getcountrystats()
        lines = ["🌍 Davlatlar bo'yicha statistika:\n"]
        for code, cnt in rows:
            flag = FLAG.get(code, "🌍")
            lines.append(f"{flag} {code}: {cnt} ta")
        await sendlong(update.message, "\n".join(lines), ADMINKB)

    elif text == "📢 Xabar yuborish":
        ud["inbcmenu"] = True
        await update.message.reply_text(
            "📢 Xabar yuborish usulini tanlang:\n\n"
            "✍️ Oddiy — matn, rasm, video, GIF...\n"
            "↩️ Forward — xabarni forward qilish\n"
            "🖼 Ko'p mediali — album (10 ta gacha)\n"
            "📅 Rejalashtirilgan — belgilangan vaqtda",
            replymarkup=BCTYPE_KB,
        )

    elif text == "✍️ Oddiy xabar":
        ud["st"] = "bc_single"
        await update.message.reply_text(
            "Yubormoqchi bolgan xabarni yuboring (matn, rasm, video, GIF, fayl...):",
            replymarkup=CANCELKB,
        )

    elif text == "↩️ Forward rejim":
        ud["st"] = "bc_forward"
        await update.message.reply_text(
            "↩️ Forward qilmoqchi bolgan xabarni forward qiling:",
            replymarkup=CANCELKB,
        )

    elif text == "🖼 Ko'p mediali reklama":
        ud["st"]       = "bcmediacollect"
        ud["bc_items"] = []
        from config import MAX_ALBUM
        await update.message.reply_text(
            f"🖼 Ko'p mediali reklama\n\n"
            f"📸/🎬 Rasm/video yuboring (max {MAX_ALBUM} ta)",
            replymarkup=MEDIACOLLECT_KB,
        )

    elif text == "📅 Rejalashtirilgan":
        bc_st = ud.get("st")
        if bcst in ("bctype", None) and ud.get("inbcmenu"):
            # Broadcast rejimida
            ud["st"] = "bcscheduledmsg"
            ud.pop("inbcmenu", None)
            await update.message.reply_text(
                "Rejalashtirilgan broadcast - yubormoqchi bolgan xabarni yuboring:",
                replymarkup=CANCELKB,
            )
        else:
            # Ro'yxatni ko'rsatish
            rows = getscheduledlist()
            if not rows:
                await update.message.reply_text(
                    "📅 Rejalashtirilgan broadcastlar yo'q.", replymarkup=ADMINKB
                )
                return
            lines = ["📅 Rejalashtirilgan xabarlar:\n"]
            for bcid, schedat, status, _ in rows:
                lines.append(f"• #{bcid} — {schedat[:16]} [{status}]")
            lines.append("\nBekor qilish uchun: /cancel_bc ID")
            await sendlong(update.message, "\n".join(lines), ADMINKB)

    elif text == "◀️ Orqaga":
        ud.clear()
        await update.message.replytext("👑 Admin panel:", replymarkup=ADMIN_KB)

    elif text == "👑 Yaqinda premium":
        rows = getpremiumrecent(30)
        if not rows:
            await update.message.replytext("Premium foydalanuvchilar yo'q.", replymarkup=ADMIN_KB)
            return
        lines = ["👑 Yaqinda premium olganlar:\n"]
        for uid, fname, uname, cnt, until in rows:
            d = datetime.fromisoformat(until).strftime("%d.%m.%Y") if until else "?"
            lines.append(
                f"• [{fname}](tg://user?id={uid}) @{uname or '—'}\n"
                f"  🛒 {cnt}× | 📅 {d}"
            )
        await sendlong(update.message, "\n".join(lines), ADMINKB)

    elif text == "🏆 Ko'p sotib olgan":
        rows = getpremiumtop(30)
        if not rows:
            await update.message.replytext("Ma'lumot yo'q.", replymarkup=ADMIN_KB)
            return
        lines = ["🏆 Eng ko'p premium olganlar:\n"]
        for i, (uid, fname, uname, cnt, _) in enumerate(rows, 1):
            m = ["🥇","🥈","🥉"][i-1] if i <= 3 else f"{i}."
            lines.append(f"{m} [{fname}](tg://user?id={uid}) @{uname or '—'} — {cnt}×")
        await sendlong(update.message, "\n".join(lines), ADMINKB)

    elif text == "✅ Premium berish":
        ud["st"] = "grant_id"
        await update.message.reply_text(
            "🆔 ID va ixtiyoriy kun kiriting:\nFormat: ID [kun]\nMisol: 123456 30",
        )

    elif text == "❌ Premium olish":
        ud["st"] = "revoke_id"
        await update.message.reply_text(
            "🆔 Premium bekor qilish uchun ID kiriting:",
        )

    elif text == "🚫 Ban":
        ud["st"] = "ban_id"
        await update.message.reply_text(
            "🆔 Ban qilish uchun ID kiriting:\nFormat: ID [sabab]",
        )

    elif text == "✅ Unban":
        ud["st"] = "unban_id"
        await update.message.reply_text(
            "🆔 Unban qilish uchun ID kiriting:",
        )

    elif text == "📋 Banlanganlar":
        rows = getbannedusers(30)
        if not rows:
            await update.message.replytext("✅ Banlangan foydalanuvchilar yo'q.", replymarkup=ADMIN_KB)
            return
        lines = ["🚫 Banlangan foydalanuvchilar:\n"]
        for uid, fname, uname, reason in rows:
            lines.append(
                f"• [{fname}](tg://user?id={uid}) @{uname or '—'}\n"
                f"  📝 {reason or 'Sabab yoq'}"
            )
        await sendlong(update.message, "\n".join(lines), ADMINKB)

    elif text == "📋 Kutayotgan to'lovlar":
        rows = getpendingpayments(20)
        if not rows:
            await update.message.replytext("✅ Kutayotgan to'lovlar yo'q.", replymarkup=ADMIN_KB)
            return
        lines = ["💳 Kutayotgan to'lovlar:\n"]
        for pid, uid, fname, uname, _, dt in rows:
            lines.append(f"• #{pid} [{fname}](tg://user?id={uid}) — {dt[:16]}")
        await sendlong(update.message, "\n".join(lines), ADMINKB)

    elif text == "💳 To'lov matni":
        ud["stedit"] = "paymenttext"
        await update.message.reply_text(
            "To'lov matni - qaysi tilni tahrirlaysiz?",
            replymarkup=LANGEDIT_KB,
        )

    elif text == "❓ Help matni":
        ud["stedit"] = "helptext"
        await update.message.reply_text(
            "Help matni - qaysi tilni tahrirlaysiz?",
            replymarkup=LANGEDIT_KB,
        )

    elif text in ("🇺🇿 O'zbek matni", "🇷🇺 Rus matni", "🇬🇧 Ingliz matni"):
        editkey = ud.get("stedit")
        if not edit_key:
            await update.message.replytext("❌ Avval matni tanlang.", replymarkup=ADMIN_KB)
            return
        lang_map = {
            "🇺🇿 O'zbek matni": "uz",
            "🇷🇺 Rus matni":     "ru",
            "🇬🇧 Ingliz matni":  "en",
        }
        lang = lang_map[text]
        state_map = {
            ("paymenttext", "uz"): "editpay_uz",
            ("paymenttext", "ru"): "editpay_ru",
            ("paymenttext", "en"): "editpay_en",
            ("helptext",    "uz"): "edithelp_uz",
            ("helptext",    "ru"): "edithelp_ru",
            ("helptext",    "en"): "edithelp_en",
        }
        ud["st"] = statemap.get((editkey, lang))
        current = getsetting(editkey).get(lang, "")
        await update.message.reply_text(
            f"📝 Joriy matn ({lang.upper()}):\n\n{current}\n\n"
            "Yangi matnni yuboring:",
            replymarkup=CANCELKB,
        )

    elif text == "🎟 Promo kodlar":
        rows = getpromolist()
        if not rows:
            await update.message.replytext("Promo kodlar yo'q.", replymarkup=ADMIN_KB)
            return
        lines = ["🎟 Promo kodlar:\n"]
        for code, days, maxu, used, active,  in rows:
            status = "✅" if active else "❌"
            maxstr = str(maxu) if max_u != -1 else "∞"
            lines.append(f"{status} {code} — {days} kun | {used}/{max_str}")
        await sendlong(update.message, "\n".join(lines), ADMINKB)

    elif text == "➕ Promo yaratish":
        ud["st"] = "promo_create"
        await update.message.reply_text(
            "🎟 Promo kod yaratish:\n\n"
            "Format: KOD KUN MAXFOYDALANISH_\n"
            "Misol: SUMMER50 30 100\n"
            "(maxfoydalanish: -1 = cheksiz)_",
        )

    else:
        await update.message.replytext("👑 Admin panel:", replymarkup=ADMIN_KB)


# ════════════════════════════════════════════════════════
#  ADMIN CALLBACK (to'lov tasdiqlash)
# ════════════════════════════════════════════════════════
async def oncallback(update: Update, context: ContextTypes.DEFAULTTYPE):
    q    = update.callback_query
    data = q.data
    u    = q.from_user
    await q.answer()

    if data.startswith("admpay:"):
        _, action, pid_str = data.split(":")
        pid = int(pid_str)
        pay = get_payment(pid)

        if not pay:
            await q.message.reply_text("❌ To'lov topilmadi.")
            return

        tid = pay[1]

        if action == "approve":
            setpaymentstatus(pid, "approved")
            until = grantpremium(tid, PREMIUMDAYS)

            from database import get_lang
            from translations import tx
            tl = get_lang(tid)
            try:
                await context.bot.send_message(
                    tid,
                    tx(tl, "pay_confirmed",
                       days=PREMIUM_DAYS, until=until.strftime("%d.%m.%Y")),
                )
            except Exception:
                pass

            new_cap = (q.message.caption or "") + \
                      f"\n\n✅ TASDIQLANDI — {u.first_name} {datetime.now().strftime('%H:%M')}"
            try:
                await q.message.editcaption(newcap)
            except Exception:
                pass

        elif action == "reject":
            setpaymentstatus(pid, "rejected")

            from database import get_lang
            from translations import tx
            tl = get_lang(tid)
            try:
                await context.bot.send_message(
                    tid, tx(tl, "pay_rejected")
                )
            except Exception:
                pass

            new_cap = (q.message.caption or "") + \
                      f"\n\n❌ RAD ETILDI — {u.first_name} {datetime.now().strftime('%H:%M')}"
            try:
                await q.message.editcaption(newcap)
            except Exception:
                pass
                
