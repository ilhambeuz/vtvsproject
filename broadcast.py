"""
📢 VTVS Bot — Broadcast
"""
import asyncio
import json
import logging
 
from telegram import InputMediaPhoto, InputMediaVideo
 
logger = logging.getLogger(__name__)
 
 
# ════════════════════════════════════════════════════════
#  PROGRESS
# ════════════════════════════════════════════════════════
async def _update_progress(msg, label: str, done: int, total: int, ok: int, fail: int):
    pct = int(done / total * 100) if total else 100
    bar = "█" * (pct // 10) + "░" * (10 - pct // 10)
    try:
        await msg.edit_text(
            f"{label}\n\n{bar} *{pct}%*\n"
            f"✅ {ok} | ❌ {fail} | 📊 {done}/{total}",
            parse_mode="Markdown",
        )
    except Exception:
        pass
 
 
# ════════════════════════════════════════════════════════
#  XABAR YUBORISH YORDAMCHISI
# ════════════════════════════════════════════════════════
def msg_to_dict(msg) -> dict:
    """Message obyektidan broadcast uchun ma'lumot olish."""
    d = {
        "type":    None,
        "file_id": None,
        "text":    msg.text or "",
        "caption": msg.caption or "",
        "fwd_chat": None,
        "fwd_mid":  None,
    }
    if msg.forward_origin:
        d["type"]     = "forward"
        d["fwd_chat"] = msg.chat.id
        d["fwd_mid"]  = msg.message_id
        return d
 
    if msg.text:
        d["type"] = "text"
    elif msg.photo:
        d["type"], d["file_id"] = "photo",      msg.photo[-1].file_id
    elif msg.video:
        d["type"], d["file_id"] = "video",      msg.video.file_id
    elif msg.document:
        d["type"], d["file_id"] = "document",   msg.document.file_id
    elif msg.animation:
        d["type"], d["file_id"] = "animation",  msg.animation.file_id
    elif msg.voice:
        d["type"], d["file_id"] = "voice",      msg.voice.file_id
    elif msg.audio:
        d["type"], d["file_id"] = "audio",      msg.audio.file_id
    elif msg.sticker:
        d["type"], d["file_id"] = "sticker",    msg.sticker.file_id
    elif msg.video_note:
        d["type"], d["file_id"] = "video_note", msg.video_note.file_id
    return d
 
 
async def _send_one(bot, uid: int, src: dict) -> bool:
    """Bitta foydalanuvchiga xabar yuborish. True=muvaffaqiyatli."""
    try:
        t   = src.get("type")
        fid = src.get("file_id")
        cap = src.get("caption", "")
        txt = src.get("text", "")
        pm  = "Markdown" if cap else None
 
        if t == "text":
            await bot.send_message(
                uid, txt, parse_mode="Markdown",
                disable_web_page_preview=True,
            )
        elif t == "photo":
            await bot.send_photo(uid, photo=fid, caption=cap, parse_mode=pm)
        elif t == "video":
            await bot.send_video(uid, video=fid, caption=cap, parse_mode=pm)
        elif t == "document":
            await bot.send_document(uid, document=fid, caption=cap, parse_mode=pm)
        elif t == "animation":
            await bot.send_animation(uid, animation=fid, caption=cap, parse_mode=pm)
        elif t == "voice":
            await bot.send_voice(uid, voice=fid, caption=cap)
        elif t == "audio":
            await bot.send_audio(uid, audio=fid, caption=cap)
        elif t == "sticker":
            await bot.send_sticker(uid, sticker=fid)
        elif t == "video_note":
            await bot.send_video_note(uid, video_note=fid)
        elif t == "forward":
            await bot.forward_message(
                chat_id=uid,
                from_chat_id=src["fwd_chat"],
                message_id=src["fwd_mid"],
            )
        return True
    except Exception:
        return False
 
 
# ════════════════════════════════════════════════════════
#  BROADCAST FUNKSIYALARI
# ════════════════════════════════════════════════════════
async def broadcast_single(bot, src: dict, uids: list, prog_msg) -> tuple[int, int]:
    """Bitta xabarni hammaga yuborish."""
    ok = fail = 0
    total = len(uids)
    label = "📢 *Yuborilmoqda...*"
 
    for i, uid in enumerate(uids):
        if await _send_one(bot, uid, src):
            ok += 1
        else:
            fail += 1
 
        if (i + 1) % 100 == 0 or (i + 1) == total:
            await _update_progress(prog_msg, label, i + 1, total, ok, fail)
        await asyncio.sleep(0.04)
 
    return ok, fail
 
 
async def broadcast_album(
    bot, items: list, caption: str, uids: list, prog_msg
) -> tuple[int, int]:
    """Ko'p mediali reklama (album)."""
    ok = fail = 0
    total = len(uids)
    label = "🖼 *Reklama yuborilmoqda...*"
 
    # InputMedia ro'yxatini bir marta tuzish
    album = []
    for idx, item in enumerate(items):
        cap_here = caption if idx == 0 else None
        pm = "Markdown" if cap_here else None
        if item["type"] == "photo":
            album.append(
                InputMediaPhoto(media=item["file_id"], caption=cap_here, parse_mode=pm)
            )
        else:
            album.append(
                InputMediaVideo(media=item["file_id"], caption=cap_here, parse_mode=pm)
            )
 
    for i, uid in enumerate(uids):
        try:
            if len(album) == 1:
                item = items[0]
                if item["type"] == "photo":
                    await bot.send_photo(
                        uid, photo=item["file_id"],
                        caption=caption,
                        parse_mode="Markdown" if caption else None,
                    )
                else:
                    await bot.send_video(
                        uid, video=item["file_id"],
                        caption=caption,
                        parse_mode="Markdown" if caption else None,
                    )
            else:
                await bot.send_media_group(uid, media=album)
            ok += 1
        except Exception:
            fail += 1
 
        if (i + 1) % 100 == 0 or (i + 1) == total:
            await _update_progress(prog_msg, label, i + 1, total, ok, fail)
        await asyncio.sleep(0.05)
 
    return ok, fail
 
 
def done_text(label: str, ok: int, fail: int, total: int, extra: str = "") -> str:
    return (
        f"✅ *{label}*\n\n"
        f"✅ Muvaffaqiyatli: *{ok}*\n"
        f"❌ Xatolik: *{fail}*\n"
        f"📊 Jami: *{total}*"
        + (f"\n{extra}" if extra else "")
    )
 
