"""
🤖 VTVS Bot v4.0 — Asosiy fayl
Ishga tushirish: python bot.py
"""
import logging
import os
import re
import datetime as dt

from telegram import Update, LabeledPrice
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    PreCheckoutQueryHandler,
    filters,
)

from config import (
    BOT_TOKEN, BOT_USERNAME, ADMIN_IDS,
    PREMIUM_DAYS, STARS_AMOUNT,
    DAILY_STATS_HOUR, EXPIRY_CHECK_HOUR, WEEKLY_STATS_DAY,
)
from database import (
    init_db, ensure_user, get_user, get_lang, set_lang,
    is_banned, is_premium, premium_until, grant_premium,
    check_limit, bump_usage, used_today,
    add_payment_screenshot, add_payment_stars,
    set_referred_by, add_bonus_days, ref_count,
    get_payment, set_payment_status,
    get_help_text, get_payment_text,
    use_promo,
)
from translations import tx
from audio import (
    extract_audio, get_duration, parse_time, fmt_time,
    yt_download_async, file_mb, _cleanup,
)
from keyboards import (
    lang_kb, main_menu_kb, premium_kb, action_kb,
    speed_kb, quality_kb, admin_pay_kb, renew_kb,
)
import admin as adm
from scheduler import (
    check_premium_expiry, send_daily_stats,
    send_weekly_stats, process_scheduled,
)

logger = logging.getLogger(__name__)
logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)

# YouTube/Instagram URL pattern
YT_RE = re.compile(
    r"https?://(www\.)?(youtube\.com|youtu\.be|instagram\.com|instagr\.am)/\S+"
)

TEMP_DIR = "temp"


# ════════════════════════════════════════════════════════
#  YORDAMCHI
# ════════════════════════════════════════════════════════
def is_admin(uid: int) -> bool:
    return uid in ADMIN_IDS


async def limit_check(update: Update, uid: int, lang: str) -> bool:
    """
    Limit tekshirish. False = limit oshdi (xabar yuborildi).
    True = foydalanish mumkin.
    """
    from config import FREE_DAILY_LIMIT
    if is_premium(uid):
        return True
    if not check_limit(uid):
        await update.message.reply_text(
            tx(lang, "limit_reached", limit=FREE_DAILY_LIMIT),
            parse_mode="Markdown",
            reply_markup=renew_kb(lang),
        )
        return False
    return True


# ════════════════════════════════════════════════════════
#  /start
# ════════════════════════════════════════════════════════
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u    = update.effective_user
    args = context.args or []
    tg_lang = u.language_code or ""

    ensure_user(u.id, u.username, u.first_name, tg_lang)

    # Ban tekshirish
    if is_banned(u.id) and not is_admin(u.id):
        await update.message.reply_text("🚫 Siz botdan foydalana olmaysiz.")
        return

    # Referral
    if args and args[0].startswith("ref_"):
        try:
            ref_id = int(args[0][4:])
            if ref_id != u.id:
                if set_referred_by(u.id, ref_id):
                    add_bonus_days(ref_id, 3)
                    from config import REFERRAL_BONUS
                    ref_lang = get_lang(ref_id)
                    try:
                        note = tx(ref_lang, "ref_bonus_note")
                        await context.bot.send_message(
                            ref_id,
                            tx(ref_lang, "ref_bonus_received",
                               name=u.first_name, bonus=3) + f"\n\n{note}",
                            parse_mode="Markdown",
                        )
                    except Exception:
                        pass
        except (ValueError, TypeError):
            pass

    # Admin → admin panel + bot foydalanishi
    if is_admin(u.id):
        from keyboards import ADMIN_KB
        await update.message.reply_text(
            f"👑 *Admin panel*\n👤 {u.first_name}",
            parse_mode="Markdown",
            reply_markup=ADMIN_KB,
        )
        return

    # Yangi foydalanuvchi → til tanlash
    row = get_user(u.id)
    if row and row[3] == "en" and not args:
        await update.message.reply_text(
            tx("uz", "choose_lang"), reply_markup=lang_kb()
        )
        return

    await _show_welcome(update, u)


async def _show_welcome(update: Update, u):
    lang = get_lang(u.id)
    prem = is_premium(u.id)
    plan = tx(lang, "premium_plan") if prem else tx(lang, "free_plan")
    from config import FREE_DAILY_LIMIT
    lim  = "∞" if prem else str(FREE_DAILY_LIMIT)
    await update.message.reply_text(
        tx(lang, "welcome",
           name=u.first_name, plan=plan,
           used=used_today(u.id), limit=lim),
        parse_mode="Markdown",
        reply_markup=main_menu_kb(lang),
    )


# ════════════════════════════════════════════════════════
#  /language
# ════════════════════════════════════════════════════════
async def cmd_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_admin(update.effective_user.id):
        return
    await update.message.reply_text(
        tx("uz", "choose_lang"), reply_markup=lang_kb()
    )


# ════════════════════════════════════════════════════════
#  /premium
# ════════════════════════════════════════════════════════
async def cmd_premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    if is_admin(u.id):
        return
    lang = get_lang(u.id)
    if is_premium(u.id):
        until = premium_until(u.id)
        await update.message.reply_text(
            tx(lang, "already_premium",
               until=until.strftime("%d.%m.%Y") if until else "?"),
            parse_mode="Markdown",
        )
        return
    pay_text = get_payment_text(lang)
    await update.message.reply_text(
        pay_text, parse_mode="Markdown", reply_markup=premium_kb(lang)
    )


# ════════════════════════════════════════════════════════
#  /referral
# ════════════════════════════════════════════════════════
async def cmd_referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    if is_admin(u.id):
        return
    lang  = get_lang(u.id)
    count = ref_count(u.id)
    row   = get_user(u.id)
    bonus = row[12] if row else 0
    link  = f"https://t.me/{BOT_USERNAME}?start=ref_{u.id}"
    await update.message.reply_text(
        tx(lang, "ref_info",
           bonus=3, link=link, count=count, days=bonus),
        parse_mode="Markdown",
    )


# ════════════════════════════════════════════════════════
#  /stats
# ════════════════════════════════════════════════════════
async def cmd_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    if is_admin(u.id):
        return
    lang = get_lang(u.id)
    prem = is_premium(u.id)
    plan = tx(lang, "premium_plan") if prem else tx(lang, "free_plan")
    from config import FREE_DAILY_LIMIT
    lim  = "∞" if prem else str(FREE_DAILY_LIMIT)
    until_dt = premium_until(u.id)
    until_tx = tx(lang, "prem_until",
                  date=until_dt.strftime("%d.%m.%Y")) if prem and until_dt \
               else tx(lang, "no_premium")
    row   = get_user(u.id)
    total = row[13] if row else 0
    since = row[16][:10] if row else "?"
    await update.message.reply_text(
        tx(lang, "my_stats",
           name=u.first_name, plan=plan, until=until_tx,
           used=used_today(u.id), limit=lim,
           total=total, refs=ref_count(u.id), since=since),
        parse_mode="Markdown",
    )


# ════════════════════════════════════════════════════════
#  /help
# ════════════════════════════════════════════════════════
async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    if is_admin(u.id):
        return
    lang = get_lang(u.id)
    text = get_help_text(lang)
    await update.message.reply_text(text, parse_mode="Markdown")


# ════════════════════════════════════════════════════════
#  /admin
# ════════════════════════════════════════════════════════
async def cmd_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    from keyboards import ADMIN_KB
    await update.message.reply_text("👑 Admin panel:", reply_markup=ADMIN_KB)


# ════════════════════════════════════════════════════════
#  /cancel_bc
# ════════════════════════════════════════════════════════
async def cmd_cancel_bc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    args = context.args
    if not args:
        await update.message.reply_text("Format: /cancel_bc ID")
        return
    try:
        from database import cancel_scheduled
        cancel_scheduled(int(args[0]))
        await update.message.reply_text(f"✅ #{args[0]} bekor qilindi.")
    except Exception as e:
        await update.message.reply_text(f"❌ {e}")


# ════════════════════════════════════════════════════════
#  VIDEO / OVOZLI XABAR / MP3 HANDLER
# ════════════════════════════════════════════════════════
async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u   = update.effective_user
    msg = update.message

    # Admin → broadcast media handler
    if is_admin(u.id):
        await adm.on_media(update, context)
        return

    # Ban tekshirish
    lang = get_lang(u.id)
    if is_banned(u.id):
        await msg.reply_text(tx(lang, "banned"))
        return

    # Limit tekshirish
    if not await limit_check(update, u.id, lang):
        return

    # Faylni aniqlash
    if msg.video:
        file, fname = msg.video, f"v_{u.id}_{msg.video.file_unique_id}.mp4"
    elif msg.video_note:
        file, fname = msg.video_note, f"vn_{u.id}_{msg.video_note.file_unique_id}.mp4"
    elif msg.voice:
        file, fname = msg.voice, f"vc_{u.id}_{msg.voice.file_unique_id}.ogg"
    elif msg.audio:
        file, fname = msg.audio, f"au_{u.id}_{msg.audio.file_unique_id}.mp3"
    elif msg.document:
        mime = msg.document.mime_type or ""
        if mime.startswith("video/") or mime.startswith("audio/") or "mp3" in mime:
            file, fname = msg.document, f"doc_{u.id}_{msg.document.file_unique_id}"
        else:
            return
    else:
        return

    src_path = os.path.join(TEMP_DIR, fname)
    status   = await msg.reply_text(tx(lang, "processing"))

    try:
        tg_file = await context.bot.get_file(file.file_id)
        await tg_file.download_to_drive(src_path)
    except Exception as e:
        logger.error("Fayl yuklab olishda xatolik: %s", e)
        await status.edit_text(tx(lang, "error"))
        return

    dur = get_duration(src_path)

    # Premium foydalanuvchi → tanlov
    prem = is_premium(u.id)
    context.user_data.update({
        "src_path": src_path,
        "src_dur":  dur,
    })

    await status.edit_text(
        tx(lang, "choose_action", dur=fmt_time(dur)),
        parse_mode="Markdown",
        reply_markup=action_kb(lang, prem),
    )


# ════════════════════════════════════════════════════════
#  MATN HANDLER
# ════════════════════════════════════════════════════════
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u    = update.effective_user
    text = update.message.text or ""
    lang = get_lang(u.id)
    ud   = context.user_data

    # Admin → admin handler
    if is_admin(u.id):
        await adm.on_text(update, context)
        return

    # Ban
    if is_banned(u.id):
        await update.message.reply_text(tx(lang, "banned"))
        return

    # URL tekshirish
    if YT_RE.search(text.strip()):
        await handle_url(update, context, text.strip())
        return

    # Trim boshlanish vaqti
    if ud.get("trim_start_wait"):
        sec = parse_time(text)
        dur = ud.get("src_dur", 0)
        if sec is None:
            await update.message.reply_text(tx(lang, "bad_time"), parse_mode="Markdown")
            return
        if dur and sec >= dur:
            await update.message.reply_text(tx(lang, "time_over", dur=fmt_time(dur)), parse_mode="Markdown")
            return
        ud.pop("trim_start_wait", None)
        ud["trim_s"]       = sec
        ud["trim_end_wait"] = True
        await update.message.reply_text(
            tx(lang, "enter_end", start=fmt_time(sec)), parse_mode="Markdown"
        )
        return

    # Trim tugash vaqti
    if ud.get("trim_end_wait"):
        await _do_trim_end(update, context, text, lang)
        return

    # Screenshot kutilmoqda
    if ud.get("await_ss"):
        await update.message.reply_text(tx(lang, "send_screenshot"), parse_mode="Markdown")
        return

    # Promo kod
    if ud.get("await_promo"):
        ud.pop("await_promo", None)
        result = use_promo(u.id, text)
        if result["ok"]:
            grant_premium(u.id, result["days"])
            await update.message.reply_text(
                tx(lang, "promo_ok", days=result["days"]),
                parse_mode="Markdown",
            )
        else:
            reason = result.get("reason", "invalid")
            key = "promo_used" if reason == "used" else "promo_invalid"
            await update.message.reply_text(tx(lang, key), parse_mode="Markdown")
        return

    await update.message.reply_text(tx(lang, "hint"))


async def _do_trim_end(update, context, text, lang):
    ud    = context.user_data
    u     = update.effective_user
    sec   = parse_time(text)
    start = ud.get("trim_s", 0)
    dur   = ud.get("src_dur", 0)
    src   = ud.get("src_path")

    if sec is None:
        await update.message.reply_text(tx(lang, "bad_time"), parse_mode="Markdown")
        return
    if sec <= start:
        await update.message.reply_text(tx(lang, "end_before_start"), parse_mode="Markdown")
        return
    if dur and sec > dur:
        await update.message.reply_text(tx(lang, "time_over", dur=fmt_time(dur)), parse_mode="Markdown")
        return
    if not src or not os.path.exists(src):
        await update.message.reply_text(tx(lang, "no_file"))
        ud.clear()
        return

    for k in ("trim_end_wait", "trim_s", "src_path", "src_dur"):
        ud.pop(k, None)

    status = await update.message.reply_text(tx(lang, "processing"))
    ok = await extract_audio(
        context.bot, u.id, src,
        start=start, end=sec, lang=lang,
    )
    if ok:
        bump_usage(u.id)
        await status.delete()
    else:
        await status.edit_text(tx(lang, "error"))

    _cleanup(src)


# ════════════════════════════════════════════════════════
#  RASM HANDLER (screenshot)
# ════════════════════════════════════════════════════════
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user

    # Admin → broadcast media
    if is_admin(u.id):
        await adm.on_media(update, context)
        return

    lang = get_lang(u.id)
    ud   = context.user_data

    if not ud.get("await_ss"):
        return

    ud.pop("await_ss", None)
    fid = update.message.photo[-1].file_id
    pid = add_payment_screenshot(u.id, fid)

    caption = (
        f"💳 *To'lov #{pid}*\n\n"
        f"👤 [{u.first_name}](tg://user?id={u.id})\n"
        f"🆔 `{u.id}`\n"
        f"📌 @{u.username or '—'}\n"
        f"🕐 {dt.datetime.now().strftime('%d.%m.%Y %H:%M')}"
    )
    for aid in ADMIN_IDS:
        try:
            await context.bot.send_photo(
                aid, photo=fid, caption=caption,
                parse_mode="Markdown",
                reply_markup=admin_pay_kb(pid),
            )
        except Exception as e:
            logger.error("Admin %s ga yuborishda xatolik: %s", aid, e)

    await update.message.reply_text(tx(lang, "screenshot_sent"), parse_mode="Markdown")


# ════════════════════════════════════════════════════════
#  CALLBACK HANDLER
# ════════════════════════════════════════════════════════
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q    = update.callback_query
    data = q.data or ""
    u    = q.from_user
    lang = get_lang(u.id)
    ud   = context.user_data

    await q.answer()  # Doim birinchi answer qilish

    # ── Admin to'lov ─────────────────────────────────
    if data.startswith("admpay:"):
        if is_admin(u.id):
            await adm.on_callback(update, context)
        return

    # ── Ban tekshirish ────────────────────────────────
    if is_banned(u.id) and not is_admin(u.id):
        return

    # ── Til tanlash ───────────────────────────────────
    if data.startswith("lang:"):
        nl = data[5:]
        set_lang(u.id, nl)
        await q.message.edit_text(tx(nl, "lang_saved"))
        prem = is_premium(u.id)
        plan = tx(nl, "premium_plan") if prem else tx(nl, "free_plan")
        from config import FREE_DAILY_LIMIT
        lim = "∞" if prem else str(FREE_DAILY_LIMIT)
        await q.message.reply_text(
            tx(nl, "welcome", name=u.first_name, plan=plan,
               used=used_today(u.id), limit=lim),
            parse_mode="Markdown",
            reply_markup=main_menu_kb(nl),
        )
        return

    # ── Asosiy menyu ──────────────────────────────────
    if data.startswith("menu:"):
        action = data[5:]

        if action == "premium":
            if is_premium(u.id):
                until_dt = premium_until(u.id)
                await q.message.reply_text(
                    tx(lang, "already_premium",
                       until=until_dt.strftime("%d.%m.%Y") if until_dt else "?"),
                    parse_mode="Markdown",
                )
                return
            pay_text = get_payment_text(lang)
            await q.message.reply_text(
                pay_text, parse_mode="Markdown", reply_markup=premium_kb(lang)
            )

        elif action == "status":
            prem = is_premium(u.id)
            plan = tx(lang, "premium_plan") if prem else tx(lang, "free_plan")
            from config import FREE_DAILY_LIMIT
            lim  = "∞" if prem else str(FREE_DAILY_LIMIT)
            until_dt = premium_until(u.id)
            until_tx = tx(lang, "prem_until",
                          date=until_dt.strftime("%d.%m.%Y")) if prem and until_dt \
                       else tx(lang, "no_premium")
            row   = get_user(u.id)
            total = row[13] if row else 0
            since = row[16][:10] if row else "?"
            await q.message.reply_text(
                tx(lang, "my_stats",
                   name=u.first_name, plan=plan, until=until_tx,
                   used=used_today(u.id), limit=lim,
                   total=total, refs=ref_count(u.id), since=since),
                parse_mode="Markdown",
            )

        elif action == "ref":
            count = ref_count(u.id)
            row   = get_user(u.id)
            bonus = row[12] if row else 0
            link  = f"https://t.me/{BOT_USERNAME}?start=ref_{u.id}"
            await q.message.reply_text(
                tx(lang, "ref_info", bonus=3, link=link, count=count, days=bonus),
                parse_mode="Markdown",
            )

        elif action == "stats":
            row   = get_user(u.id)
            total = row[13] if row else 0
            since = row[16][:10] if row else "?"
            prem  = is_premium(u.id)
            plan  = tx(lang, "premium_plan") if prem else tx(lang, "free_plan")
            from config import FREE_DAILY_LIMIT
            lim   = "∞" if prem else str(FREE_DAILY_LIMIT)
            until_dt = premium_until(u.id)
            until_tx = tx(lang, "prem_until",
                          date=until_dt.strftime("%d.%m.%Y")) if prem and until_dt \
                       else tx(lang, "no_premium")
            await q.message.reply_text(
                tx(lang, "my_stats",
                   name=u.first_name, plan=plan, until=until_tx,
                   used=used_today(u.id), limit=lim,
                   total=total, refs=ref_count(u.id), since=since),
                parse_mode="Markdown",
            )

        elif action == "lang":
            await q.message.reply_text(
                tx(lang, "choose_lang"), reply_markup=lang_kb()
            )
        return

    # ── To'lov ───────────────────────────────────────
    if data.startswith("pay:"):
        method = data[4:]

        if method == "stars":
            try:
                await context.bot.send_invoice(
                    chat_id=u.id,
                    title=tx(lang, "stars_invoice_title"),
                    description=tx(lang, "stars_invoice_desc"),
                    payload=f"premium_{u.id}",
                    provider_token="",       # Stars uchun bo'sh
                    currency="XTR",
                    prices=[LabeledPrice("Premium 30 kun", STARS_AMOUNT)],
                )
            except Exception as e:
                logger.error("Stars invoice xatolik: %s", e)
                await q.message.reply_text(tx(lang, "error"))

        elif method == "screenshot":
            ud["await_ss"] = True
            await q.message.reply_text(
                tx(lang, "send_screenshot"), parse_mode="Markdown"
            )

        elif method == "promo":
            ud["await_promo"] = True
            await q.message.reply_text(
                tx(lang, "enter_promo"), parse_mode="Markdown"
            )
        return

    # ── Action (video qayta ishlash) ──────────────────
    if data.startswith("action:"):
        act = data[7:]
        src = ud.get("src_path")
        dur = ud.get("src_dur")

        if act == "back":
            if src:
                await q.message.edit_text(
                    tx(lang, "choose_action", dur=fmt_time(dur)),
                    parse_mode="Markdown",
                    reply_markup=action_kb(lang, is_premium(u.id)),
                )
            return

        if not src or not os.path.exists(src):
            await q.message.reply_text(tx(lang, "no_file"))
            ud.clear()
            return

        if act == "full":
            ud_src = ud.pop("src_path", None)
            ud.pop("src_dur", None)
            await q.message.edit_text(tx(lang, "processing"))
            ok = await extract_audio(context.bot, u.id, ud_src, lang=lang)
            if ok:
                bump_usage(u.id)
                await q.message.delete()
            else:
                await q.message.edit_text(tx(lang, "error"))
            _cleanup(ud_src)

        elif act == "trim":
            ud["trim_start_wait"] = True
            await q.message.edit_text(
                tx(lang, "enter_start", dur=fmt_time(dur)),
                parse_mode="Markdown",
            )

        elif act == "speed":
            if not is_premium(u.id):
                await q.message.reply_text(
                    "⭐ Speed o'zgartirish faqat Premium uchun!",
                    reply_markup=renew_kb(lang),
                )
                return
            await q.message.edit_text(
                tx(lang, "choose_speed"),
                parse_mode="Markdown",
                reply_markup=speed_kb(lang),
            )

        elif act == "vocal":
            if not is_premium(u.id):
                await q.message.reply_text(
                    "⭐ Vocal ajratish faqat Premium uchun!",
                    reply_markup=renew_kb(lang),
                )
                return
            ud_src = ud.pop("src_path", None)
            ud.pop("src_dur", None)
            await q.message.edit_text(tx(lang, "processing"))
            ok = await extract_audio(context.bot, u.id, ud_src, vocal=True, lang=lang)
            if ok:
                bump_usage(u.id)
                await q.message.delete()
            else:
                await q.message.edit_text(tx(lang, "error"))
            _cleanup(ud_src)

        elif act == "noise":
            if not is_premium(u.id):
                await q.message.reply_text(
                    "⭐ Shovqin yo'qotish faqat Premium uchun!",
                    reply_markup=renew_kb(lang),
                )
                return
            ud_src = ud.pop("src_path", None)
            ud.pop("src_dur", None)
            await q.message.edit_text(tx(lang, "processing"))
            ok = await extract_audio(context.bot, u.id, ud_src, noise=True, lang=lang)
            if ok:
                bump_usage(u.id)
                await q.message.delete()
            else:
                await q.message.edit_text(tx(lang, "error"))
            _cleanup(ud_src)
        return

    # ── Tezlik tanlash ────────────────────────────────
    if data.startswith("speed:"):
        speed_val = float(data[6:])
        src = ud.pop("src_path", None)
        ud.pop("src_dur", None)
        if not src or not os.path.exists(src):
            await q.message.reply_text(tx(lang, "no_file"))
            return
        await q.message.edit_text(tx(lang, "processing"))
        ok = await extract_audio(
            context.bot, u.id, src, speed=speed_val, lang=lang
        )
        if ok:
            bump_usage(u.id)
            await q.message.delete()
        else:
            await q.message.edit_text(tx(lang, "error"))
        _cleanup(src)
        return

    # ── YouTube/Instagram sifat ───────────────────────
    if data.startswith("yt:"):
        quality = data[3:]
        url     = ud.pop("yt_url", None)
        if not url:
            await q.message.edit_text(tx(lang, "error"))
            return

        prem = is_premium(u.id)
        if not prem and quality not in ("360", "audio"):
            await q.message.edit_text(
                tx(lang, "free_quality_only"),
                parse_mode="Markdown",
                reply_markup=renew_kb(lang),
            )
            return

        if not await _check_limit_cb(q, u.id, lang):
            return

        await q.message.edit_text(tx(lang, "downloading"))

        try:
            dl_path = await yt_download_async(url, quality, u.id)
        except Exception as e:
            logger.error("yt_download_async xatolik: %s", e)
            await q.message.edit_text(tx(lang, "error"))
            return

        if not dl_path or not os.path.exists(dl_path):
            await q.message.edit_text(tx(lang, "error"))
            return

        size = file_mb(dl_path)
        if size > 49 and quality != "audio":
            await q.message.edit_text(
                tx(lang, "yt_too_big", size=round(size, 1))
            )
            _cleanup(dl_path)
            return

        await q.message.edit_text(tx(lang, "processing"))

        try:
            if quality != "audio":
                with open(dl_path, "rb") as f:
                    await context.bot.send_video(
                        u.id, video=f,
                        caption=f"🎬 {quality}p",
                        supports_streaming=True,
                    )
            ok = await extract_audio(context.bot, u.id, dl_path, lang=lang)
            if ok:
                bump_usage(u.id)
                await q.message.delete()
            else:
                await q.message.edit_text(tx(lang, "error"))
        except Exception as e:
            logger.error("Yuborishda xatolik: %s", e)
            await q.message.edit_text(tx(lang, "error"))
        finally:
            _cleanup(dl_path)
        return


async def _check_limit_cb(q, uid: int, lang: str) -> bool:
    """Callback uchun limit tekshirish."""
    from config import FREE_DAILY_LIMIT
    if is_premium(uid):
        return True
    if not check_limit(uid):
        await q.message.edit_text(
            tx(lang, "limit_reached", limit=FREE_DAILY_LIMIT),
            parse_mode="Markdown",
            reply_markup=renew_kb(lang),
        )
        return False
    return True


# ════════════════════════════════════════════════════════
#  URL HANDLER
# ════════════════════════════════════════════════════════
async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE, url: str):
    u    = update.effective_user
    lang = get_lang(u.id)
    msgs = {
        "uz": "⏳ YouTube/Instagram yuklab olish hozircha texnik ishlar sababli vaqtincha ochirilib turibdi. Tez orada qayta ishga tushiriladi!",

        "ru": "⏳ Загрузка YouTube/Instagram временно отключена по техническим причинам. Скоро снова заработает!",

        "en": "⏳ YouTube/Instagram downloading is temporarily disabled due to maintenance. It will be back soon!",
    }
    await update.message.reply_text(msgs.get(lang, msgs["en"]))


# ════════════════════════════════════════════════════════
#  TELEGRAM STARS TO'LOV
# ════════════════════════════════════════════════════════
async def pre_checkout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.pre_checkout_query.answer(ok=True)


async def successful_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u      = update.effective_user
    lang   = get_lang(u.id)
    charge = update.message.successful_payment

    add_payment_stars(u.id, charge.telegram_payment_charge_id, charge.total_amount)
    until = grant_premium(u.id, PREMIUM_DAYS)

    await update.message.reply_text(
        tx(lang, "stars_success",
           days=PREMIUM_DAYS, until=until.strftime("%d.%m.%Y")),
        parse_mode="Markdown",
    )
    logger.info("Stars to'lov: user=%s, amount=%s", u.id, charge.total_amount)


# ════════════════════════════════════════════════════════
#  MAIN
# ════════════════════════════════════════════════════════
def main():
    init_db()

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # ── Komandalar ────────────────────────────────────
    app.add_handler(CommandHandler("start",     cmd_start))
    app.add_handler(CommandHandler("premium",   cmd_premium))
    app.add_handler(CommandHandler("referral",  cmd_referral))
    app.add_handler(CommandHandler("language",  cmd_language))
    app.add_handler(CommandHandler("stats",     cmd_stats))
    app.add_handler(CommandHandler("help",      cmd_help))
    app.add_handler(CommandHandler("admin",     cmd_admin))
    app.add_handler(CommandHandler("cancel_bc", cmd_cancel_bc))

    # ── Callback ──────────────────────────────────────
    app.add_handler(CallbackQueryHandler(handle_callback))

    # ── Media (video, ovoz, mp3, document) ───────────
    app.add_handler(MessageHandler(
        filters.VIDEO | filters.VIDEO_NOTE | filters.VOICE |
        filters.AUDIO |
        filters.Document.MimeType("video/mp4") |
        filters.Document.MimeType("video/webm") |
        filters.Document.MimeType("video/quicktime") |
        filters.Document.MimeType("audio/mpeg") |
        filters.Document.MimeType("audio/mp3"),
        handle_media,
    ))

    # ── Rasm ─────────────────────────────────────────
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    # ── Matn ─────────────────────────────────────────
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # ── Stars to'lov ─────────────────────────────────
    app.add_handler(PreCheckoutQueryHandler(pre_checkout))
    app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment))

    # ── Scheduler ────────────────────────────────────
    jq = app.job_queue

    # Har kuni premium tugash tekshiruvi
    jq.run_daily(
        check_premium_expiry,
        time=dt.time(hour=EXPIRY_CHECK_HOUR, minute=0),
    )
    # Har kuni statistika
    jq.run_daily(
        send_daily_stats,
        time=dt.time(hour=DAILY_STATS_HOUR, minute=0),
    )
    # Har haftada statistika (dushanba)
    jq.run_daily(
        send_weekly_stats,
        time=dt.time(hour=DAILY_STATS_HOUR, minute=30),
        days=(WEEKLY_STATS_DAY,),
    )
    # Har 5 daqiqada rejalashtirilgan broadcastlar
    jq.run_repeating(process_scheduled, interval=300, first=30)

    logger.info("🚀 VTVS Bot v4.0 ishga tushdi!")
    app.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True,
    )


if __name__ == "__main__":
    main()
