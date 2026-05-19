"""
👑 VTVS Bot — Admin panel handlerlari
"""
import json
import logging
from datetime import datetime

from telegram import Update
from telegram.ext import ContextTypes

from config import ADMIN_IDS, PREMIUM_DAYS
from database import (
    get_stats, get_country_stats,
    get_premium_recent, get_premium_top,
    grant_premium, revoke_premium,
    ban_user, unban_user, get_banned_users,
    get_pending_payments, set_payment_status, get_payment,
    get_setting, set_setting,
    create_promo, get_promo_list, toggle_promo,
    save_scheduled_bc, get_scheduled_list, cancel_scheduled,
    all_user_ids,
)
from broadcast import broadcast_single, broadcast_album, msg_to_dict, done_text
from keyboards import (
    ADMIN_KB, BC_TYPE_KB, MEDIA_COLLECT_KB, CONFIRM_KB,
    CAPTION_KB, LANG_EDIT_KB, CANCEL_KB,
    admin_pay_kb,
)

logger = logging.getLogger(__name__)

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
            p, parse_mode="Markdown",
            reply_markup=kb if i == len(parts) - 1 else None,
        )


# ════════════════════════════════════════════════════════
#  ADMIN MEDIA HANDLER
# ════════════════════════════════════════════════════════
async def on_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin rasm/video yuborganda."""
    msg = update.message
    ud  = context.user_data
    st  = ud.get("st")

    if st == "bc_media_collect":
        items = ud.setdefault("bc_items", [])
        from config import MAX_ALBUM
        if len(items) >= MAX_ALBUM:
            await msg.reply_text(
                f"⚠️ Maksimal {MAX_ALBUM} ta. '✅ Reklama tayyor' bosing.",
                reply_markup=MEDIA_COLLECT_KB,
            )
            return

        if msg.photo:
            items.append({"type": "photo", "file_id": msg.photo[-1].file_id})
            icon = "📸"
        elif msg.video:
            items.append({"type": "video", "file_id": msg.video.file_id})
            icon = "🎬"
        else:
            await msg.reply_text("⚠️ Faqat 📸 yoki 🎬 yuboring.", reply_markup=MEDIA_COLLECT_KB)
            return

        n = len(items)
        await msg.reply_text(
            f"{icon} *{n}/10* qo'shildi.\n" +
            ("Yana qo'shing yoki 'Tayyor' bosing." if n < MAX_ALBUM
             else "Limit to'ldi. '✅ Tayyor' bosing."),
            parse_mode="Markdown",
            reply_markup=MEDIA_COLLECT_KB,
        )
        return

    if st in ("bc_single", "bc_forward"):
        src = msg_to_dict(msg)
        uids = all_user_ids()
        ud["st"]  = f"{st}_confirm"
        ud["src"] = src
        await msg.reply_text(
            f"📢 *Tasdiqlang:*\n\n"
            f"📌 Tur: *{src['type']}*\n"
            f"👥 Yuboriladi: *{len(uids)}* ta",
            parse_mode="Markdown",
            reply_markup=CONFIRM_KB,
        )


# ════════════════════════════════════════════════════════
#  ADMIN TEXT HANDLER
# ════════════════════════════════════════════════════════
async def on_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""
    ud   = context.user_data
    bot  = context.bot
    st   = ud.get("st")

    # ── Universal bekor qilish ────────────────────────
    if text == "❌ Bekor":
        ud.clear()
        await update.message.reply_text("❌ Bekor qilindi.", reply_markup=ADMIN_KB)
        return

    # ════════════════════════════════════════════════
    #  BROADCAST STATE MACHINE
    # ════════════════════════════════════════════════

    if st == "bc_media_collect" and text == "✅ Reklama tayyor":
        items = ud.get("bc_items", [])
        if not items:
            await update.message.reply_text("⚠️ Hali hech narsa yo'q.", reply_markup=MEDIA_COLLECT_KB)
            return
        ud["st"] = "bc_caption"
        await update.message.reply_text(
            f"✅ *{len(items)} ta media qo'shildi!*\n\n"
            "📝 Matn (caption) yuboring yoki '⏭ Caption yo'q' bosing.",
            parse_mode="Markdown",
            reply_markup=CAPTION_KB,
        )
        return

    if st == "bc_caption":
        caption = "" if text == "⏭ Caption yo'q" else text
        items   = ud.get("bc_items", [])
        uids    = all_user_ids()
        ud["st"]         = "bc_album_confirm"
        ud["bc_caption"] = caption
        p = sum(1 for x in items if x["type"] == "photo")
        v = sum(1 for x in items if x["type"] == "video")
        cap_prev = (caption[:60] + "...") if len(caption) > 60 else caption
        await update.message.reply_text(
            f"🖼 *Tasdiqlang:*\n\n"
            f"📸 {p} rasm | 🎬 {v} video\n"
            f"📝 _{cap_prev or 'Yoq'}_\n"
            f"👥 *{len(uids)}* ta foydalanuvchi\n\nYuborilsinmi?",
            parse_mode="Markdown",
            reply_markup=CONFIRM_KB,
        )
        return

    if st in ("bc_single", "bc_forward") and text not in ("✅ Ha, yubor",):
        # Matnli xabar
        src  = msg_to_dict(update.message)
        uids = all_user_ids()
        ud["st"]  = f"{st}_confirm"
        ud["src"] = src
        prev = (text[:80] + "...") if len(text) > 80 else text
        await update.message.reply_text(
            f"✍️ *Tasdiqlang:*\n\n_{prev}_\n\n👥 *{len(uids)}* ta",
            parse_mode="Markdown",
            reply_markup=CONFIRM_KB,
        )
        return

    # ── HA, YUBOR ────────────────────────────────────
    if text == "✅ Ha, yubor":
        if st == "bc_single_confirm":
            src  = ud.pop("src", {})
            ud.clear()
            uids = all_user_ids()
            prog = await update.message.reply_text(
                f"📢 Yuborilmoqda... 0/{len(uids)}", reply_markup=ADMIN_KB
            )
            ok, fail = await broadcast_single(bot, src, uids, prog)
            await prog.edit_text(
                done_text("Xabar yuborildi!", ok, fail, len(uids)),
                parse_mode="Markdown",
            )
            return

        if st == "bc_forward_confirm":
            src  = ud.pop("src", {})
            ud.clear()
            uids = all_user_ids()
            prog = await update.message.reply_text(
                f"↩️ Forward qilinmoqda... 0/{len(uids)}", reply_markup=ADMIN_KB
            )
            ok, fail = await broadcast_single(bot, src, uids, prog)
            await prog.edit_text(
                done_text("Forward yuborildi!", ok, fail, len(uids)),
                parse_mode="Markdown",
            )
            return

        if st == "bc_album_confirm":
            items   = ud.pop("bc_items", [])
            caption = ud.pop("bc_caption", "")
            ud.clear()
            uids = all_user_ids()
            prog = await update.message.reply_text(
                f"🖼 Reklama yuborilmoqda... 0/{len(uids)}", reply_markup=ADMIN_KB
            )
            ok, fail = await broadcast_album(bot, items, caption, uids, prog)
            await prog.edit_text(
                done_text("Reklama yuborildi!", ok, fail, len(uids),
                          extra=f"🖼 Media: *{len(items)}* ta"),
                parse_mode="Markdown",
            )
            return

        if st == "bc_scheduled_confirm":
            src  = ud.pop("src", {})
            sdt  = ud.pop("sched_dt", "")
            uid  = update.effective_user.id
            ud.clear()
            bc_id = save_scheduled_bc(src, sdt, uid)
            await update.message.reply_text(
                f"✅ *Rejalashtirildi!*\n📅 {sdt[:16]}\n🆔 #{bc_id}",
                parse_mode="Markdown",
                reply_markup=ADMIN_KB,
            )
            return

    # ════════════════════════════════════════════════
    #  TO'LOV MATNI TAHRIRLASH
    # ════════════════════════════════════════════════
    if st in ("edit_pay_uz", "edit_pay_ru", "edit_pay_en"):
        lang_map = {"edit_pay_uz": "uz", "edit_pay_ru": "ru", "edit_pay_en": "en"}
        lang = lang_map[st]
        set_setting("payment_text", lang, text)
        ud.clear()
        await update.message.reply_text(
            f"✅ To'lov matni saqlandi! ({lang.upper()})", reply_markup=ADMIN_KB
        )
        return

    if st in ("edit_help_uz", "edit_help_ru", "edit_help_en"):
        lang_map = {"edit_help_uz": "uz", "edit_help_ru": "ru", "edit_help_en": "en"}
        lang = lang_map[st]
        set_setting("help_text", lang, text)
        ud.clear()
        await update.message.reply_text(
            f"✅ Help matni saqlandi! ({lang.upper()})", reply_markup=ADMIN_KB
        )
        return

    # ════════════════════════════════════════════════
    #  PROMO KOD YARATISH
    # ════════════════════════════════════════════════
    if st == "promo_create":
        # Format: KOD 30 100  (kod, kun, max_uses)
        parts = text.strip().split()
        try:
            code = parts[0].upper()
            days = int(parts[1]) if len(parts) > 1 else PREMIUM_DAYS
            max_u = int(parts[2]) if len(parts) > 2 else -1
            ok = create_promo(code, days, max_u)
            ud.clear()
            if ok:
                await update.message.reply_text(
                    f"✅ Promo kod yaratildi!\n"
                    f"🎟 Kod: `{code}`\n"
                    f"📅 Kunlar: *{days}*\n"
                    f"👥 Max foydalanish: {'Cheksiz' if max_u == -1 else max_u}",
                    parse_mode="Markdown",
                    reply_markup=ADMIN_KB,
                )
            else:
                await update.message.reply_text(
                    "❌ Bu kod allaqachon mavjud.", reply_markup=ADMIN_KB
                )
        except (IndexError, ValueError):
            await update.message.reply_text(
                "❌ Format: `KOD 30 100`\n_kod kun max_uses_",
                parse_mode="Markdown",
            )
        return

    # ════════════════════════════════════════════════
    #  REJALASHTIRILGAN BROADCAST
    # ════════════════════════════════════════════════
    if st == "bc_scheduled_msg":
        src = msg_to_dict(update.message)
        ud["st"]  = "bc_scheduled_dt"
        ud["src"] = src
        await update.message.reply_text(
            "📅 *Yuborish vaqtini kiriting:*\n"
            "_Format: `DD.MM.YYYY HH:MM`_\n"
            "_Misol: `25.12.2025 10:00`_",
            parse_mode="Markdown",
        )
        return

    if st == "bc_scheduled_dt":
        try:
            dt = datetime.strptime(text.strip(), "%d.%m.%Y %H:%M")
            if dt <= datetime.now():
                await update.message.reply_text("❌ Vaqt o'tib ketgan. Kelajak vaqt kiriting.")
                return
            ud["sched_dt"] = dt.isoformat()
            ud["st"]       = "bc_scheduled_confirm"
            uids = all_user_ids()
            await update.message.reply_text(
                f"📅 *Tasdiqlang:*\n\n"
                f"🕐 Vaqt: *{text.strip()}*\n"
                f"👥 *{len(uids)}* ta foydalanuvchi\n\nYuborilsinmi?",
                parse_mode="Markdown",
                reply_markup=CONFIRM_KB,
            )
        except ValueError:
            await update.message.reply_text(
                "❌ Format noto'g'ri. Misol: `25.12.2025 10:00`",
                parse_mode="Markdown",
            )
        return

    # ════════════════════════════════════════════════
    #  BAN / UNBAN
    # ════════════════════════════════════════════════
    if st == "ban_id":
        try:
            parts = text.strip().split(None, 1)
            tid    = int(parts[0])
            reason = parts[1] if len(parts) > 1 else ""
            ban_user(tid, update.effective_user.id, reason)
            ud.clear()
            await update.message.reply_text(
                f"🚫 Foydalanuvchi ban qilindi.\n🆔 `{tid}`",
                parse_mode="Markdown", reply_markup=ADMIN_KB,
            )
            try:
                await bot.send_message(tid, "🚫 Siz botdan ban qilindingiz.")
            except Exception:
                pass
        except (ValueError, IndexError):
            await update.message.reply_text("❌ Format: ID [sabab]")
        return

    if st == "unban_id":
        try:
            tid = int(text.strip())
            unban_user(tid, update.effective_user.id)
            ud.clear()
            await update.message.reply_text(
                f"✅ Foydalanuvchi unban qilindi.\n🆔 `{tid}`",
                parse_mode="Markdown", reply_markup=ADMIN_KB,
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
    if st == "grant_id":
        try:
            parts = text.strip().split()
            tid   = int(parts[0])
            days  = int(parts[1]) if len(parts) > 1 else PREMIUM_DAYS
            until = grant_premium(tid, days)
            ud.clear()
            await update.message.reply_text(
                f"✅ Premium berildi!\n🆔 `{tid}`\n"
                f"📅 *{until.strftime('%d.%m.%Y')}* gacha",
                parse_mode="Markdown", reply_markup=ADMIN_KB,
            )
            from database import get_lang
            tl = get_lang(tid)
            from translations import tx
            try:
                await bot.send_message(
                    tid,
                    tx(tl, "pay_confirmed", days=days, until=until.strftime("%d.%m.%Y")),
                    parse_mode="Markdown",
                )
            except Exception:
                pass
        except (ValueError, IndexError):
            await update.message.reply_text("❌ Format: ID [kunlar]")
        return

    if st == "revoke_id":
        try:
            tid = int(text.strip())
            revoke_premium(tid)
            ud.clear()
            await update.message.reply_text(
                f"✅ Premium bekor qilindi.\n🆔 `{tid}`",
                parse_mode="Markdown", reply_markup=ADMIN_KB,
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
            f"📊 *BOT STATISTIKASI*\n{'━'*26}\n"
            f"👥 Jami: *{s['total']}*\n"
            f"🟢 Aktiv (7 kun): *{s['active']}*\n"
            f"🔴 Nofaol: *{s['inactive']}*\n"
            f"⭐ Premium: *{s['premium']}*\n"
            f"🚫 Banned: *{s['banned']}*\n"
            f"{'━'*26}\n"
            f"📅 Bugun yangi: *+{s['new_today']}*\n"
            f"📅 Hafta: *+{s['new_week']}*\n"
            f"📅 Oy: *+{s['new_month']}*\n"
            f"{'━'*26}\n"
            f"💳 Kutayotgan to'lovlar: *{s['pending_pays']}*",
            parse_mode="Markdown", reply_markup=ADMIN_KB,
        )

    elif text == "🌍 Davlatlar":
        rows = get_country_stats()
        lines = ["🌍 *Davlatlar bo'yicha statistika:*\n"]
        for code, cnt in rows:
            flag = FLAG.get(code, "🌍")
            lines.append(f"{flag} `{code}`: *{cnt}* ta")
        await send_long(update.message, "\n".join(lines), ADMIN_KB)

    elif text == "📢 Xabar yuborish":
        await update.message.reply_text(
            "📢 *Xabar yuborish usulini tanlang:*\n\n"
            "✍️ Oddiy — matn, rasm, video, GIF...\n"
            "↩️ Forward — xabarni forward qilish\n"
            "🖼 Ko'p mediali — album (10 ta gacha)\n"
            "📅 Rejalashtirilgan — belgilangan vaqtda",
            parse_mode="Markdown",
            reply_markup=BC_TYPE_KB,
        )

    elif text == "✍️ Oddiy xabar":
        ud["st"] = "bc_single"
        await update.message.reply_text(
            "✍️ *Yubormoqchi bo'lgan xabarni yuboring:*\n"
            "_(Matn, rasm, video, GIF, fayl...)_",
            parse_mode="Markdown",
            reply_markup=CANCEL_KB,
        )

    elif text == "↩️ Forward rejim":
        ud["st"] = "bc_forward"
        await update.message.reply_text(
            "↩️ *Forward qilmoqchi bo'lgan xabarni forward qiling:*",
            parse_mode="Markdown",
            reply_markup=CANCEL_KB,
        )

    elif text == "🖼 Ko'p mediali reklama":
        ud["st"]       = "bc_media_collect"
        ud["bc_items"] = []
        from config import MAX_ALBUM
        await update.message.reply_text(
            f"🖼 *Ko'p mediali reklama*\n\n"
            f"📸/🎬 Rasm/video yuboring (max {MAX_ALBUM} ta)",
            parse_mode="Markdown",
            reply_markup=MEDIA_COLLECT_KB,
        )

    elif text == "📅 Rejalashtirilgan":
        if ud.get("st") == "bc_type":
            # Broadcast rejimida
            ud["st"] = "bc_scheduled_msg"
            await update.message.reply_text(
                "📅 *Rejalashtirilgan broadcast*\n\nYubormoqchi bo'lgan xabarni yuboring:",
                parse_mode="Markdown",
                reply_markup=CANCEL_KB,
            )
        else:
            # Ro'yxatni ko'rsatish
            rows = get_scheduled_list()
            if not rows:
                await update.message.reply_text(
                    "📅 Rejalashtirilgan broadcastlar yo'q.", reply_markup=ADMIN_KB
                )
                return
            lines = ["📅 *Rejalashtirilgan xabarlar:*\n"]
            for bc_id, sched_at, status, _ in rows:
                lines.append(f"• #{bc_id} — {sched_at[:16]} [{status}]")
            lines.append("\nBekor qilish uchun: `/cancel_bc ID`")
            await send_long(update.message, "\n".join(lines), ADMIN_KB)

    elif text == "◀️ Orqaga":
        ud.clear()
        await update.message.reply_text("👑 Admin panel:", reply_markup=ADMIN_KB)

    elif text == "👑 Yaqinda premium":
        rows = get_premium_recent(30)
        if not rows:
            await update.message.reply_text("Premium foydalanuvchilar yo'q.", reply_markup=ADMIN_KB)
            return
        lines = ["👑 *Yaqinda premium olganlar:*\n"]
        for uid, fname, uname, cnt, until in rows:
            d = datetime.fromisoformat(until).strftime("%d.%m.%Y") if until else "?"
            lines.append(
                f"• [{fname}](tg://user?id={uid}) @{uname or '—'}\n"
                f"  🛒 {cnt}× | 📅 {d}"
            )
        await send_long(update.message, "\n".join(lines), ADMIN_KB)

    elif text == "🏆 Ko'p sotib olgan":
        rows = get_premium_top(30)
        if not rows:
            await update.message.reply_text("Ma'lumot yo'q.", reply_markup=ADMIN_KB)
            return
        lines = ["🏆 *Eng ko'p premium olganlar:*\n"]
        for i, (uid, fname, uname, cnt, _) in enumerate(rows, 1):
            m = ["🥇","🥈","🥉"][i-1] if i <= 3 else f"{i}."
            lines.append(f"{m} [{fname}](tg://user?id={uid}) @{uname or '—'} — *{cnt}×*")
        await send_long(update.message, "\n".join(lines), ADMIN_KB)

    elif text == "✅ Premium berish":
        ud["st"] = "grant_id"
        await update.message.reply_text(
            "🆔 *ID va ixtiyoriy kun kiriting:*\n_Format: `ID [kun]`_\n_Misol: `123456 30`_",
            parse_mode="Markdown",
        )

    elif text == "❌ Premium olish":
        ud["st"] = "revoke_id"
        await update.message.reply_text(
            "🆔 *Premium bekor qilish uchun ID kiriting:*",
            parse_mode="Markdown",
        )

    elif text == "🚫 Ban":
        ud["st"] = "ban_id"
        await update.message.reply_text(
            "🆔 *Ban qilish uchun ID kiriting:*\n_Format: `ID [sabab]`_",
            parse_mode="Markdown",
        )

    elif text == "✅ Unban":
        ud["st"] = "unban_id"
        await update.message.reply_text(
            "🆔 *Unban qilish uchun ID kiriting:*",
            parse_mode="Markdown",
        )

    elif text == "📋 Banlanganlar":
        rows = get_banned_users(30)
        if not rows:
            await update.message.reply_text("✅ Banlangan foydalanuvchilar yo'q.", reply_markup=ADMIN_KB)
            return
        lines = ["🚫 *Banlangan foydalanuvchilar:*\n"]
        for uid, fname, uname, reason in rows:
            lines.append(
                f"• [{fname}](tg://user?id={uid}) @{uname or '—'}\n"
                f"  📝 _{reason or 'Sabab yoq'}_"
            )
        await send_long(update.message, "\n".join(lines), ADMIN_KB)

    elif text == "📋 Kutayotgan to'lovlar":
        rows = get_pending_payments(20)
        if not rows:
            await update.message.reply_text("✅ Kutayotgan to'lovlar yo'q.", reply_markup=ADMIN_KB)
            return
        lines = ["💳 *Kutayotgan to'lovlar:*\n"]
        for pid, uid, fname, uname, _, dt in rows:
            lines.append(f"• #{pid} [{fname}](tg://user?id={uid}) — {dt[:16]}")
        await send_long(update.message, "\n".join(lines), ADMIN_KB)

    elif text == "💳 To'lov matni":
        ud["st_edit"] = "payment_text"
        await update.message.reply_text(
            "💳 *To'lov matni — qaysi til?*",
            parse_mode="Markdown",
            reply_markup=LANG_EDIT_KB,
        )

    elif text == "❓ Help matni":
        ud["st_edit"] = "help_text"
        await update.message.reply_text(
            "❓ *Help matni — qaysi til?*",
            parse_mode="Markdown",
            reply_markup=LANG_EDIT_KB,
        )

    elif text in ("🇺🇿 O'zbek matni", "🇷🇺 Rus matni", "🇬🇧 Ingliz matni"):
        edit_key = ud.get("st_edit")
        if not edit_key:
            await update.message.reply_text("❌ Avval matni tanlang.", reply_markup=ADMIN_KB)
            return
        lang_map = {
            "🇺🇿 O'zbek matni": "uz",
            "🇷🇺 Rus matni":     "ru",
            "🇬🇧 Ingliz matni":  "en",
        }
        lang = lang_map[text]
        state_map = {
            ("payment_text", "uz"): "edit_pay_uz",
            ("payment_text", "ru"): "edit_pay_ru",
            ("payment_text", "en"): "edit_pay_en",
            ("help_text",    "uz"): "edit_help_uz",
            ("help_text",    "ru"): "edit_help_ru",
            ("help_text",    "en"): "edit_help_en",
        }
        ud["st"] = state_map.get((edit_key, lang))
        current = get_setting(edit_key).get(lang, "")
        await update.message.reply_text(
            f"📝 *Joriy matn ({lang.upper()}):*\n\n{current}\n\n"
            "Yangi matnni yuboring:",
            parse_mode="Markdown",
            reply_markup=CANCEL_KB,
        )

    elif text == "🎟 Promo kodlar":
        rows = get_promo_list()
        if not rows:
            await update.message.reply_text("Promo kodlar yo'q.", reply_markup=ADMIN_KB)
            return
        lines = ["🎟 *Promo kodlar:*\n"]
        for code, days, max_u, used, active, _ in rows:
            status = "✅" if active else "❌"
            max_str = str(max_u) if max_u != -1 else "∞"
            lines.append(f"{status} `{code}` — {days} kun | {used}/{max_str}")
        await send_long(update.message, "\n".join(lines), ADMIN_KB)

    elif text == "➕ Promo yaratish":
        ud["st"] = "promo_create"
        await update.message.reply_text(
            "🎟 *Promo kod yaratish:*\n\n"
            "_Format: `KOD KUN MAX_FOYDALANISH`_\n"
            "_Misol: `SUMMER50 30 100`_\n"
            "_(max_foydalanish: -1 = cheksiz)_",
            parse_mode="Markdown",
        )

    else:
        await update.message.reply_text("👑 Admin panel:", reply_markup=ADMIN_KB)


# ════════════════════════════════════════════════════════
#  ADMIN CALLBACK (to'lov tasdiqlash)
# ════════════════════════════════════════════════════════
async def on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
            set_payment_status(pid, "approved")
            until = grant_premium(tid, PREMIUM_DAYS)

            from database import get_lang
            from translations import tx
            tl = get_lang(tid)
            try:
                await context.bot.send_message(
                    tid,
                    tx(tl, "pay_confirmed",
                       days=PREMIUM_DAYS, until=until.strftime("%d.%m.%Y")),
                    parse_mode="Markdown",
                )
            except Exception:
                pass

            new_cap = (q.message.caption or "") + \
                      f"\n\n✅ TASDIQLANDI — {u.first_name} {datetime.now().strftime('%H:%M')}"
            try:
                await q.message.edit_caption(new_cap, parse_mode="Markdown")
            except Exception:
                pass

        elif action == "reject":
            set_payment_status(pid, "rejected")

            from database import get_lang
            from translations import tx
            tl = get_lang(tid)
            try:
                await context.bot.send_message(
                    tid, tx(tl, "pay_rejected"), parse_mode="Markdown"
                )
            except Exception:
                pass

            new_cap = (q.message.caption or "") + \
                      f"\n\n❌ RAD ETILDI — {u.first_name} {datetime.now().strftime('%H:%M')}"
            try:
                await q.message.edit_caption(new_cap, parse_mode="Markdown")
            except Exception:
                pass
