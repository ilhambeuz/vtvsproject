"""
Admin panel handlerlari - Markdown ishlatilmagan
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
    create_promo, get_promo_list,
    save_scheduled_bc, get_scheduled_list, cancel_scheduled,
    all_user_ids,
)
from broadcast import broadcast_single, broadcast_album, msg_to_dict, done_text
from keyboards import (
    ADMIN_KB, BC_TYPE_KB, MEDIA_COLLECT_KB, CONFIRM_KB,
    CAPTION_KB, LANG_EDIT_KB, CANCEL_KB, admin_pay_kb,
)

logger = logging.getLogger(__name__)

FLAG = {
    "uz": "Ozbekiston", "ru": "Rossiya", "en": "Ingliz",
    "tr": "Turkiya", "fa": "Eron", "ar": "Arab",
    "id": "Indoneziya", "de": "Germaniya", "fr": "Fransiya",
    "unknown": "Noma'lum",
}


def _is_menu_btn(text):
    menu_words = [
        "Statistika", "Davlatlar", "Xabar yuborish", "Rejalashtirilgan",
        "premium", "Ban", "Unban", "Banlanganlar", "lovlar", "matni",
        "Help matni", "Promo", "Oddiy xabar", "Forward", "mediali",
        "Orqaga", "Bekor", "Ha, yubor", "Caption", "matni",
    ]
    for w in menu_words:
        if w in text:
            return True
    return False


async def send_long(msg, text, kb, chunk=4000):
    parts = [text[i:i+chunk] for i in range(0, len(text), chunk)]
    for i, p in enumerate(parts):
        await msg.reply_text(p, reply_markup=kb if i == len(parts)-1 else None)


async def on_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    ud  = context.user_data
    st  = ud.get("st")

    if st == "bc_media_collect":
        items = ud.setdefault("bc_items", [])
        from config import MAX_ALBUM
        if len(items) >= MAX_ALBUM:
            await msg.reply_text("Maximum " + str(MAX_ALBUM) + " ta.", reply_markup=MEDIA_COLLECT_KB)
            return
        if msg.photo:
            items.append({"type": "photo", "file_id": msg.photo[-1].file_id})
            icon = "Rasm"
        elif msg.video:
            items.append({"type": "video", "file_id": msg.video.file_id})
            icon = "Video"
        else:
            await msg.reply_text("Faqat rasm yoki video.", reply_markup=MEDIA_COLLECT_KB)
            return
        n = len(items)
        await msg.reply_text(
            icon + " qoshildi! " + str(n) + "/" + str(MAX_ALBUM),
            reply_markup=MEDIA_COLLECT_KB,
        )
        return

    if st in ("bc_single", "bc_forward"):
        src  = msg_to_dict(msg)
        uids = all_user_ids()
        ud["st"]  = st + "_confirm"
        ud["src"] = src
        await msg.reply_text(
            "Tasdiqlang:\nTur: " + str(src.get("type","?")) + "\nYuboriladi: " + str(len(uids)) + " ta",
            reply_markup=CONFIRM_KB,
        )


async def on_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""
    ud   = context.user_data
    bot  = context.bot
    st   = ud.get("st")

    if "Bekor" in text and len(text) < 20:
        ud.clear()
        await update.message.reply_text("Bekor qilindi.", reply_markup=ADMIN_KB)
        return

    if st == "bc_media_collect" and "Reklama tayyor" in text:
        items = ud.get("bc_items", [])
        if not items:
            await update.message.reply_text("Hali hech narsa yoq!", reply_markup=MEDIA_COLLECT_KB)
            return
        ud["st"] = "bc_caption"
        await update.message.reply_text(
            str(len(items)) + " ta media qoshildi! Reklama matnini yuboring yoki Caption yoq bosing.",
            reply_markup=CAPTION_KB,
        )
        return

    if st == "bc_caption":
        caption = "" if "Caption" in text else text
        items   = ud.get("bc_items", [])
        uids    = all_user_ids()
        ud["st"]         = "bc_album_confirm"
        ud["bc_caption"] = caption
        p = sum(1 for x in items if x["type"] == "photo")
        v = sum(1 for x in items if x["type"] == "video")
        await update.message.reply_text(
            "Tasdiqlang:\nRasm: " + str(p) + " | Video: " + str(v) +
            "\nYuboriladi: " + str(len(uids)) + " ta",
            reply_markup=CONFIRM_KB,
        )
        return

    if st in ("bc_single", "bc_forward") and "Ha, yubor" not in text:
        if not _is_menu_btn(text):
            src  = msg_to_dict(update.message)
            uids = all_user_ids()
            ud["st"]  = st + "_confirm"
            ud["src"] = src
            prev = text[:80] + "..." if len(text) > 80 else text
            await update.message.reply_text(
                "Tasdiqlang:\n" + prev + "\nYuboriladi: " + str(len(uids)) + " ta",
                reply_markup=CONFIRM_KB,
            )
            return

    if "Ha, yubor" in text:
        if st == "bc_single_confirm":
            src  = ud.pop("src", {})
            ud.clear()
            uids = all_user_ids()
            prog = await update.message.reply_text("Yuborilmoqda... 0/" + str(len(uids)), reply_markup=ADMIN_KB)
            ok, fail = await broadcast_single(bot, src, uids, prog)
            await prog.edit_text(done_text("Xabar yuborildi!", ok, fail, len(uids)))
            return

        if st == "bc_forward_confirm":
            src  = ud.pop("src", {})
            ud.clear()
            uids = all_user_ids()
            prog = await update.message.reply_text("Forward qilinmoqda... 0/" + str(len(uids)), reply_markup=ADMIN_KB)
            ok, fail = await broadcast_single(bot, src, uids, prog)
            await prog.edit_text(done_text("Forward yuborildi!", ok, fail, len(uids)))
            return

        if st == "bc_album_confirm":
            items   = ud.pop("bc_items", [])
            caption = ud.pop("bc_caption", "")
            ud.clear()
            uids = all_user_ids()
            prog = await update.message.reply_text("Reklama yuborilmoqda... 0/" + str(len(uids)), reply_markup=ADMIN_KB)
            ok, fail = await broadcast_album(bot, items, caption, uids, prog)
            await prog.edit_text(done_text("Reklama yuborildi!", ok, fail, len(uids)))
            return

        if st == "bc_scheduled_confirm":
            src  = ud.pop("src", {})
            sdt  = ud.pop("sched_dt", "")
            uid  = update.effective_user.id
            ud.clear()
            bc_id = save_scheduled_bc(src, sdt, uid)
            await update.message.reply_text("Rejalashtirildi! ID: " + str(bc_id), reply_markup=ADMIN_KB)
            return

    if st in ("edit_pay_uz", "edit_pay_ru", "edit_pay_en"):
        lang = {"edit_pay_uz": "uz", "edit_pay_ru": "ru", "edit_pay_en": "en"}[st]
        set_setting("payment_text", lang, text)
        ud.clear()
        await update.message.reply_text("Tolov matni saqlandi! (" + lang.upper() + ")", reply_markup=ADMIN_KB)
        return

    if st in ("edit_help_uz", "edit_help_ru", "edit_help_en"):
        lang = {"edit_help_uz": "uz", "edit_help_ru": "ru", "edit_help_en": "en"}[st]
        set_setting("help_text", lang, text)
        ud.clear()
        await update.message.reply_text("Help matni saqlandi! (" + lang.upper() + ")", reply_markup=ADMIN_KB)
        return

    if st == "promo_create" and not _is_menu_btn(text):
        parts = text.strip().split()
        try:
            code  = parts[0].upper()
            days  = int(parts[1]) if len(parts) > 1 else PREMIUM_DAYS
            max_u = int(parts[2]) if len(parts) > 2 else -1
            ok    = create_promo(code, days, max_u)
            ud.clear()
            max_str = "Cheksiz" if max_u == -1 else str(max_u)
            msg_txt = ("Promo kod yaratildi!\nKod: " + code + "\nKunlar: " + str(days) + "\nMax: " + max_str) if ok else "Bu kod allaqachon mavjud."
            await update.message.reply_text(msg_txt, reply_markup=ADMIN_KB)
        except (IndexError, ValueError):
            await update.message.reply_text("Format: KOD 30 100\nMisol: SUMMER50 30 100")
        return

    if st == "bc_scheduled_msg":
        src = msg_to_dict(update.message)
        ud["st"]  = "bc_scheduled_dt"
        ud["src"] = src
        await update.message.reply_text("Vaqtni kiriting:\nFormat: KK.OO.YYYY SS:MM\nMisol: 25.12.2025 10:00")
        return

    if st == "bc_scheduled_dt":
        try:
            dt = datetime.strptime(text.strip(), "%d.%m.%Y %H:%M")
            if dt <= datetime.now():
                await update.message.reply_text("Vaqt otib ketgan!")
                return
            ud["sched_dt"] = dt.isoformat()
            ud["st"]       = "bc_scheduled_confirm"
            uids = all_user_ids()
            await update.message.reply_text(
                "Tasdiqlang:\nVaqt: " + text.strip() + "\nYuboriladi: " + str(len(uids)) + " ta",
                reply_markup=CONFIRM_KB,
            )
        except ValueError:
            await update.message.reply_text("Format notogri. Misol: 25.12.2025 10:00")
        return

    if st == "ban_id" and not _is_menu_btn(text):
        try:
            parts  = text.strip().split(None, 1)
            tid    = int(parts[0])
            reason = parts[1] if len(parts) > 1 else ""
            ban_user(tid, update.effective_user.id, reason)
            ud.clear()
            await update.message.reply_text("Ban qilindi. ID: " + str(tid), reply_markup=ADMIN_KB)
            try:
                await bot.send_message(tid, "Siz botdan ban qilindingiz.")
            except Exception:
                pass
        except (ValueError, IndexError):
            await update.message.reply_text("Format: ID [sabab]")
        return

    if st == "unban_id" and not _is_menu_btn(text):
        try:
            tid = int(text.strip())
            unban_user(tid, update.effective_user.id)
            ud.clear()
            await update.message.reply_text("Unban qilindi. ID: " + str(tid), reply_markup=ADMIN_KB)
            try:
                await bot.send_message(tid, "Baningiz olib tashlandi.")
            except Exception:
                pass
        except ValueError:
            await update.message.reply_text("Faqat ID kiriting.")
        return

    if st == "grant_id" and not _is_menu_btn(text):
        try:
            parts = text.strip().split()
            tid   = int(parts[0])
            days  = int(parts[1]) if len(parts) > 1 else PREMIUM_DAYS
            until = grant_premium(tid, days)
            ud.clear()
            await update.message.reply_text(
                "Premium berildi! ID: " + str(tid) + "\n" + until.strftime("%d.%m.%Y") + " gacha",
                reply_markup=ADMIN_KB,
            )
            from database import get_lang
            from translations import tx
            tl = get_lang(tid)
            try:
                await bot.send_message(tid, tx(tl, "pay_confirmed", days=days, until=until.strftime("%d.%m.%Y")))
            except Exception:
                pass
        except (ValueError, IndexError):
            await update.message.reply_text("Format: ID [kunlar]")
        return

    if st == "revoke_id" and not _is_menu_btn(text):
        try:
            tid = int(text.strip())
            revoke_premium(tid)
            ud.clear()
            await update.message.reply_text("Premium bekor qilindi. ID: " + str(tid), reply_markup=ADMIN_KB)
        except ValueError:
            await update.message.reply_text("Faqat ID kiriting.")
        return

    if "zbek matni" in text:
        edit_key = ud.get("st_edit")
        if edit_key:
            ud["st"] = "edit_pay_uz" if edit_key == "payment_text" else "edit_help_uz"
            current  = get_setting(edit_key).get("uz", "")
            await update.message.reply_text("Joriy (UZ):\n" + current + "\n\nYangi matnni yuboring:", reply_markup=CANCEL_KB)
        return

    if "Rus matni" in text:
        edit_key = ud.get("st_edit")
        if edit_key:
            ud["st"] = "edit_pay_ru" if edit_key == "payment_text" else "edit_help_ru"
            current  = get_setting(edit_key).get("ru", "")
            await update.message.reply_text("Joriy (RU):\n" + current + "\n\nYangi matnni yuboring:", reply_markup=CANCEL_KB)
        return

    if "Ingliz matni" in text:
        edit_key = ud.get("st_edit")
        if edit_key:
            ud["st"] = "edit_pay_en" if edit_key == "payment_text" else "edit_help_en"
            current  = get_setting(edit_key).get("en", "")
            await update.message.reply_text("Joriy (EN):\n" + current + "\n\nYangi matnni yuboring:", reply_markup=CANCEL_KB)
        return

    if "Statistika" in text and "Davlatlar" not in text:
        s = get_stats()
        await update.message.reply_text(
            "BOT STATISTIKASI\n" + "="*20 + "\n"
            "Jami: " + str(s["total"]) + "\n"
            "Aktiv (7 kun): " + str(s["active"]) + "\n"
            "Nofaol: " + str(s["inactive"]) + "\n"
            "Premium: " + str(s["premium"]) + "\n"
            "Banned: " + str(s["banned"]) + "\n" + "="*20 + "\n"
            "Bugun yangi: +" + str(s["new_today"]) + "\n"
            "Hafta: +" + str(s["new_week"]) + "\n"
            "Oy: +" + str(s["new_month"]) + "\n" + "="*20 + "\n"
            "Kutayotgan tolovlar: " + str(s["pending_pays"]),
            reply_markup=ADMIN_KB,
        )

    elif "Davlatlar" in text:
        rows  = get_country_stats()
        lines = ["Davlatlar statistikasi:\n"]
        for code, cnt in rows:
            name = FLAG.get(code, code)
            lines.append(name + " (" + code + "): " + str(cnt) + " ta")
        await send_long(update.message, "\n".join(lines), ADMIN_KB)

    elif "Xabar yuborish" in text:
        ud["in_bc_menu"] = True
        await update.message.reply_text(
            "Xabar yuborish usulini tanlang:",
            reply_markup=BC_TYPE_KB,
        )

    elif "Oddiy xabar" in text:
        ud["st"] = "bc_single"
        await update.message.reply_text("Yubormoqchi bolgan xabarni yuboring:", reply_markup=CANCEL_KB)

    elif "Forward rejim" in text:
        ud["st"] = "bc_forward"
        await update.message.reply_text("Forward qilmoqchi bolgan xabarni forward qiling:", reply_markup=CANCEL_KB)

    elif "mediali reklama" in text:
        ud["st"]       = "bc_media_collect"
        ud["bc_items"] = []
        from config import MAX_ALBUM
        await update.message.reply_text(
            "Ko'p mediali reklama\nRasm va/yoki video yuboring (max " + str(MAX_ALBUM) + " ta):",
            reply_markup=MEDIA_COLLECT_KB,
        )

    elif "Rejalashtirilgan" in text:
        if ud.get("in_bc_menu"):
            ud["st"] = "bc_scheduled_msg"
            ud.pop("in_bc_menu", None)
            await update.message.reply_text("Rejalashtirilgan broadcast - xabarni yuboring:", reply_markup=CANCEL_KB)
        else:
            rows = get_scheduled_list()
            if not rows:
                await update.message.reply_text("Rejalashtirilgan broadcastlar yoq.", reply_markup=ADMIN_KB)
                return
            lines = ["Rejalashtirilgan xabarlar:\n"]
            for bc_id, sched_at, status, _ in rows:
                lines.append("#" + str(bc_id) + " - " + sched_at[:16] + " [" + status + "]")
            await send_long(update.message, "\n".join(lines), ADMIN_KB)

    elif "Orqaga" in text:
        ud.clear()
        await update.message.reply_text("Admin panel:", reply_markup=ADMIN_KB)

    elif "Yaqinda premium" in text:
        rows = get_premium_recent(30)
        if not rows:
            await update.message.reply_text("Premium foydalanuvchilar yoq.", reply_markup=ADMIN_KB)
            return
        lines = ["Yaqinda premium olganlar:\n"]
        for uid, fname, uname, cnt, until in rows:
            d = datetime.fromisoformat(until).strftime("%d.%m.%Y") if until else "?"
            lines.append("- " + str(fname) + " (tg://user?id=" + str(uid) + ") @" + str(uname or "-") + " | " + str(cnt) + "x | " + d)
        await send_long(update.message, "\n".join(lines), ADMIN_KB)

    elif "sotib olgan" in text:
        rows = get_premium_top(30)
        if not rows:
            await update.message.reply_text("Ma'lumot yoq.", reply_markup=ADMIN_KB)
            return
        lines = ["Eng kop premium olganlar:\n"]
        for i, (uid, fname, uname, cnt, _) in enumerate(rows, 1):
            lines.append(str(i) + ". " + str(fname) + " (tg://user?id=" + str(uid) + ") @" + str(uname or "-") + " - " + str(cnt) + "x")
        await send_long(update.message, "\n".join(lines), ADMIN_KB)

    elif "Premium berish" in text:
        ud["st"] = "grant_id"
        await update.message.reply_text("ID va ixtiyoriy kun kiriting:\nMisol: 123456 30")

    elif "Premium olish" in text:
        ud["st"] = "revoke_id"
        await update.message.reply_text("Premium bekor qilish uchun ID kiriting:")

    elif text.strip() == "Ban" or ("Ban" in text and "Unban" not in text and "Banlanganlar" not in text and len(text) < 10):
        ud["st"] = "ban_id"
        await update.message.reply_text("Ban qilish uchun ID kiriting:\nFormat: ID [sabab]")

    elif "Unban" in text:
        ud["st"] = "unban_id"
        await update.message.reply_text("Unban qilish uchun ID kiriting:")

    elif "Banlanganlar" in text:
        rows = get_banned_users(30)
        if not rows:
            await update.message.reply_text("Banlangan foydalanuvchilar yoq.", reply_markup=ADMIN_KB)
            return
        lines = ["Banlangan foydalanuvchilar:\n"]
        for uid, fname, uname, reason in rows:
            lines.append("- " + str(fname) + " (tg://user?id=" + str(uid) + ") @" + str(uname or "-") + " | " + str(reason or "Sabab yoq"))
        await send_long(update.message, "\n".join(lines), ADMIN_KB)

    elif "Kutayotgan" in text:
        rows = get_pending_payments(20)
        if not rows:
            await update.message.reply_text("Kutayotgan tolovlar yoq.", reply_markup=ADMIN_KB)
            return
        lines = ["Kutayotgan tolovlar:\n"]
        for pid, uid, fname, uname, _, dt in rows:
            lines.append("#" + str(pid) + " " + str(fname or "?") + " (tg://user?id=" + str(uid) + ") - " + dt[:16])
        await send_long(update.message, "\n".join(lines), ADMIN_KB)

    elif "lov matni" in text:
        ud["st_edit"] = "payment_text"
        await update.message.reply_text("Tolov matni - qaysi tilni tahrirlaysiz?", reply_markup=LANG_EDIT_KB)

    elif "Help matni" in text:
        ud["st_edit"] = "help_text"
        await update.message.reply_text("Help matni - qaysi tilni tahrirlaysiz?", reply_markup=LANG_EDIT_KB)

    elif "Promo kodlar" in text and "yaratish" not in text:
        rows = get_promo_list()
        if not rows:
            await update.message.reply_text("Promo kodlar yoq.", reply_markup=ADMIN_KB)
            return
        lines = ["Promo kodlar:\n"]
        for code, days, max_u, used, active, _ in rows:
            status  = "Aktiv" if active else "Nofaol"
            max_str = str(max_u) if max_u != -1 else "Cheksiz"
            lines.append(status + " | " + code + " - " + str(days) + " kun | " + str(used) + "/" + max_str)
        await send_long(update.message, "\n".join(lines), ADMIN_KB)

    elif "Promo yaratish" in text:
        ud["st"] = "promo_create"
        await update.message.reply_text("Promo kod yaratish:\nFormat: KOD KUN MAX\nMisol: SUMMER50 30 100")

    else:
        await update.message.reply_text("Admin panel:", reply_markup=ADMIN_KB)


async def on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q    = update.callback_query
    data = q.data
    u    = q.from_user
    await q.answer()

    if not data.startswith("admpay:"):
        return

    parts  = data.split(":")
    action = parts[1]
    pid    = int(parts[2])
    pay    = get_payment(pid)

    if not pay:
        await q.message.reply_text("Tolov topilmadi.")
        return

    tid = pay[1]

    if action == "approve":
        set_payment_status(pid, "approved")
        until = grant_premium(tid, PREMIUM_DAYS)
        from database import get_lang
        from translations import tx
        tl = get_lang(tid)
        try:
            await context.bot.send_message(tid, tx(tl, "pay_confirmed", days=PREMIUM_DAYS, until=until.strftime("%d.%m.%Y")))
        except Exception:
            pass
        new_cap = (q.message.caption or "") + "\n\nTASDIQLANDI - " + u.first_name + " " + datetime.now().strftime("%H:%M")
        try:
            await q.message.edit_caption(new_cap)
        except Exception:
            pass

    elif action == "reject":
        set_payment_status(pid, "rejected")
        from database import get_lang
        from translations import tx
        tl = get_lang(tid)
        try:
            await context.bot.send_message(tid, tx(tl, "pay_rejected"))
        except Exception:
            pass
        new_cap = (q.message.caption or "") + "\n\nRAD ETILDI - " + u.first_name + " " + datetime.now().strftime("%H:%M")
        try:
            await q.message.edit_caption(new_cap)
        except Exception:
            pass
