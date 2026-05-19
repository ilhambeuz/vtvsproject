"""
⏰ VTVS Bot — Scheduler
Premium tugash ogohlantiruvi, statistika, rejalashtirilgan broadcast.
"""
import json
import logging
from datetime import datetime

from config import ADMIN_IDS, PREMIUM_DAYS
from database import (
    get_expiring_soon,
    get_stats,
    get_pending_scheduled,
    mark_scheduled_sent,
    all_user_ids,
)
from keyboards import renew_kb
from broadcast import _send_one

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════
#  PREMIUM TUGASH OGOHLANTIRUVI
# ════════════════════════════════════════════════════════
async def check_premium_expiry(context):
    """Har kuni ishga tushadi. 3 kun qolgan foydalanuvchilarga xabar."""
    bot   = context.bot
    users = get_expiring_soon(days_before=3)

    if not users:
        return

    for user_id, first_name, lang, prem_until in users:
        try:
            until_dt   = datetime.fromisoformat(prem_until)
            days_left  = (until_dt - datetime.now()).days + 1
            until_str  = until_dt.strftime("%d.%m.%Y")

            from translations import tx
            text = tx(lang, "premium_expiring",
                      days=days_left, until=until_str)

            await bot.send_message(
                user_id,
                text,
                parse_mode="Markdown",
                reply_markup=renew_kb(lang),
            )
            logger.info("Premium expiry notice sent to %s", user_id)
        except Exception as e:
            logger.error("Expiry notice xatolik %s: %s", user_id, e)


# ════════════════════════════════════════════════════════
#  KUNLIK STATISTIKA ADMINGA
# ════════════════════════════════════════════════════════
async def send_daily_stats(context):
    """Har kuni adminga statistika yuboradi."""
    bot  = context.bot
    s    = get_stats()
    now  = datetime.now().strftime("%d.%m.%Y")

    text = (
        f"📊 *Kunlik statistika — {now}*\n"
        f"{'━'*24}\n"
        f"👥 Jami: *{s['total']}*\n"
        f"🟢 Aktiv (7 kun): *{s['active']}*\n"
        f"🔴 Nofaol: *{s['inactive']}*\n"
        f"⭐ Premium: *{s['premium']}*\n"
        f"🚫 Banned: *{s['banned']}*\n"
        f"{'━'*24}\n"
        f"📅 Bugun yangi: *+{s['new_today']}*\n"
        f"💳 Kutayotgan to'lovlar: *{s['pending_pays']}*"
    )

    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, text, parse_mode="Markdown")
        except Exception as e:
            logger.error("Daily stats xatolik admin %s: %s", admin_id, e)


# ════════════════════════════════════════════════════════
#  HAFTALIK STATISTIKA
# ════════════════════════════════════════════════════════
async def send_weekly_stats(context):
    """Har haftada adminga statistika yuboradi."""
    bot  = context.bot
    s    = get_stats()
    now  = datetime.now().strftime("%d.%m.%Y")

    text = (
        f"📊 *Haftalik statistika — {now}*\n"
        f"{'━'*24}\n"
        f"👥 Jami foydalanuvchi: *{s['total']}*\n"
        f"🟢 Aktiv (7 kun): *{s['active']}*\n"
        f"⭐ Premium: *{s['premium']}*\n"
        f"{'━'*24}\n"
        f"📅 Yangi bu hafta: *+{s['new_week']}*\n"
        f"📅 Yangi bu oy: *+{s['new_month']}*"
    )

    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, text, parse_mode="Markdown")
        except Exception as e:
            logger.error("Weekly stats xatolik admin %s: %s", admin_id, e)


# ════════════════════════════════════════════════════════
#  REJALASHTIRILGAN BROADCAST
# ════════════════════════════════════════════════════════
async def process_scheduled(context):
    """Har 5 daqiqada tekshiradi va vaqti kelgan broadcastlarni yuboradi."""
    bot      = context.bot
    pending  = get_pending_scheduled()

    for bc_id, msg_data_str, scheduled_at, _ in pending:
        try:
            msg_data = json.loads(msg_data_str)
            uids     = all_user_ids()
            ok = fail = 0

            for uid in uids:
                if await _send_one(bot, uid, msg_data):
                    ok += 1
                else:
                    fail += 1

            mark_scheduled_sent(bc_id)

            # Adminga natija
            result = (
                f"✅ *Rejalashtirilgan xabar yuborildi!*\n"
                f"📅 Vaqt: {scheduled_at[:16]}\n"
                f"✅ {ok} | ❌ {fail} | 📊 {len(uids)}"
            )
            for admin_id in ADMIN_IDS:
                try:
                    await bot.send_message(admin_id, result, parse_mode="Markdown")
                except Exception:
                    pass

            logger.info("Scheduled broadcast #%s sent: %s/%s", bc_id, ok, len(uids))

        except Exception as e:
            logger.error("Scheduled broadcast #%s xatolik: %s", bc_id, e)
