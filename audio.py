"""
🎵 VTVS Bot — Audio/Video qayta ishlash
ffmpeg + yt-dlp asosida.
"""
import asyncio
import logging
import os
import subprocess
from config import TEMP_DIR, MAX_TG_MB, USE_DEMUCS

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════
#  YORDAMCHI
# ════════════════════════════════════════════════════════
def get_duration(path: str):
    """Fayl davomiyligini soniyada qaytaradi."""
    try:
        res = subprocess.run(
            ["ffprobe", "-v", "error",
             "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", path],
            capture_output=True, text=True, check=True,
        )
        return float(res.stdout.strip())
    except Exception:
        return None


def fmt_time(sec) -> str:
    """Soniyani M:SS yoki H:MM:SS formatiga."""
    if sec is None:
        return "?"
    h, rem = divmod(int(sec), 3600)
    m, s   = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def parse_time(text: str):
    """'1:30', '90', '1:30:00' → soniya. Xato bo'lsa None."""
    text = text.strip()
    try:
        if ":" in text:
            p = text.split(":")
            if len(p) == 2:
                return int(p[0]) * 60 + float(p[1])
            if len(p) == 3:
                return int(p[0]) * 3600 + int(p[1]) * 60 + float(p[2])
        return float(text)
    except (ValueError, IndexError):
        return None


def file_mb(path: str) -> float:
    return os.path.getsize(path) / 1_048_576


def _run_ffmpeg(args: list, timeout: int = 300) -> bool:
    """ffmpeg ni ishlatadi. True=muvaffaqiyatli."""
    try:
        result = subprocess.run(
            ["ffmpeg", "-y"] + args,
            capture_output=True,
            timeout=timeout,
        )
        if result.returncode != 0:
            logger.error("ffmpeg xatolik: %s", result.stderr.decode(errors="replace")[-500:])
            return False
        return True
    except subprocess.TimeoutExpired:
        logger.error("ffmpeg timeout")
        return False
    except FileNotFoundError:
        logger.error("ffmpeg topilmadi. Uni o'rnating: sudo apt install ffmpeg")
        return False


def _tmp(uid: int, suffix: str) -> str:
    return os.path.join(TEMP_DIR, f"{uid}_{suffix}")


# ════════════════════════════════════════════════════════
#  AUDIO CHIQARISH (asosiy funksiya)
# ════════════════════════════════════════════════════════
async def extract_audio(
    bot,
    chat_id: int,
    src_path: str,
    *,
    start: float = None,
    end: float   = None,
    speed: float = None,
    noise: bool  = False,
    vocal: bool  = False,
    lang: str    = "en",
) -> bool:
    """
    src_path dan ovoz ajratib voice + mp3 yuboradi.
    Parametrlar:
        start / end  : trim (soniyada)
        speed        : tezlik (0.5–2.0)
        noise        : shovqin yo'qotish
        vocal        : vocal ajratish
    """
    base     = f"{chat_id}_{os.path.splitext(os.path.basename(src_path))[0]}"
    ogg_path = _tmp(chat_id, f"{base}.ogg")
    mp3_path = _tmp(chat_id, f"{base}.mp3")

    # ── Audio filtrlar ────────────────────────────────
    filters = []
    if noise:
        filters.append("afftdn=nf=-25")
    if speed and speed != 1.0:
        # atempo faqat 0.5–2.0 ni qabul qiladi
        if 0.5 <= speed <= 2.0:
            filters.append(f"atempo={speed}")
        elif speed < 0.5:
            filters += ["atempo=0.5", f"atempo={round(speed/0.5, 3)}"]
        else:  # speed > 2.0 bo'lmaydi (max 2.0)
            filters.append("atempo=2.0")

    af = ["-af", ",".join(filters)] if filters else []

    # ── Trim argumentlari ──────────────────────────────
    trim = []
    if start is not None:
        trim += ["-ss", str(start)]
    if end is not None and start is not None:
        trim += ["-t", str(end - start)]

    # ── Vocal ajratish (alohida yo'l) ──────────────────
    if vocal:
        vocal_path = await _isolate_vocals(src_path, chat_id)
        if vocal_path:
            src_path = vocal_path
            trim = []  # Vocal allaqachon qayta ishlangan
        # Vocal ajratilmasa oddiy extract qilinadi

    # ── OGG (voice uchun) ──────────────────────────────
    ok1 = _run_ffmpeg(
        ["-i", src_path] + trim + af +
        ["-vn", "-acodec", "libopus", "-ar", "48000", "-ac", "1", "-b:a", "64k", ogg_path]
    )

    # ── MP3 ───────────────────────────────────────────
    ok2 = _run_ffmpeg(
        ["-i", src_path] + trim + af +
        ["-vn", "-acodec", "libmp3lame", "-ar", "44100", "-ac", "2", "-b:a", "192k", mp3_path]
    )

    if not (ok1 and ok2):
        _cleanup(ogg_path, mp3_path)
        return False

    # ── Caption lar ────────────────────────────────────
    from translations import tx
    if vocal:
        cap_v, cap_a = tx(lang, "voice_vocal"), tx(lang, "mp3_vocal")
    elif noise:
        cap_v, cap_a = tx(lang, "voice_noise"), tx(lang, "mp3_noise")
    elif speed and speed != 1.0:
        cap_v = tx(lang, "voice_speed", speed=speed)
        cap_a = tx(lang, "mp3_speed",   speed=speed)
    elif start is not None:
        cap_v = tx(lang, "voice_trim", s=fmt_time(start), e=fmt_time(end))
        cap_a = tx(lang, "mp3_trim",   s=fmt_time(start), e=fmt_time(end))
    else:
        cap_v, cap_a = tx(lang, "voice_full"), tx(lang, "mp3_full")

    # ── Yuborish ──────────────────────────────────────
    try:
        with open(ogg_path, "rb") as f:
            await bot.send_voice(chat_id, voice=f, caption=cap_v)
        with open(mp3_path, "rb") as f:
            await bot.send_audio(
                chat_id, audio=f, caption=cap_a,
                filename=f"{base}.mp3",
            )
    except Exception as e:
        logger.error("Yuborishda xatolik: %s", e)
        _cleanup(ogg_path, mp3_path)
        return False

    _cleanup(ogg_path, mp3_path)

    # Vocal uchun vaqtinchalik fayl
    if vocal and "vocal_path" in dir() and vocal_path:
        _cleanup(vocal_path)

    return True


# ════════════════════════════════════════════════════════
#  VOCAL AJRATISH
# ════════════════════════════════════════════════════════
async def _isolate_vocals(src_path: str, uid: int) -> str | None:
    """
    Vokal ajratadi. USE_DEMUCS=True bo'lsa demucs, aks holda ffmpeg.
    Muvaffaqiyatli bo'lsa audio fayl yo'lini, aks holda None.
    """
    if USE_DEMUCS:
        return await _vocal_demucs(src_path, uid)
    return _vocal_ffmpeg(src_path, uid)


async def _vocal_demucs(src_path: str, uid: int) -> str | None:
    """demucs yordamida vocal ajratish (sifatli)."""
    out_dir = TEMP_DIR
    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, lambda: subprocess.run(
            ["python", "-m", "demucs", "--two-stems=vocals", "-o", out_dir, src_path],
            capture_output=True, timeout=300,
        ))
        if result.returncode != 0:
            logger.error("demucs xatolik: %s", result.stderr.decode(errors="replace")[-300:])
            return _vocal_ffmpeg(src_path, uid)  # Fallback

        base     = os.path.splitext(os.path.basename(src_path))[0]
        wav_path = os.path.join(out_dir, "htdemucs", base, "vocals.wav")
        if not os.path.exists(wav_path):
            return _vocal_ffmpeg(src_path, uid)

        # wav → mp3
        out_mp3 = _tmp(uid, f"vocal_{base}.mp3")
        if _run_ffmpeg(["-i", wav_path, "-acodec", "libmp3lame", "-b:a", "192k", out_mp3]):
            _cleanup(wav_path)
            return out_mp3
        return None
    except Exception as e:
        logger.error("demucs exception: %s", e)
        return _vocal_ffmpeg(src_path, uid)


def _vocal_ffmpeg(src_path: str, uid: int) -> str | None:
    """
    ffmpeg bilan taxminiy vocal ajratish.
    Stereo markaz kanali (vokalar odatda markaz) ajratiladi +
    vocal chastota oralig'i (200–3500 Hz) filtrlanadi.
    """
    base    = os.path.splitext(os.path.basename(src_path))[0]
    out_mp3 = _tmp(uid, f"vocal_{base}.mp3")
    ok = _run_ffmpeg([
        "-i", src_path,
        "-af", (
            "pan=mono|c0=0.5*c0+0.5*c1,"  # Stereo → mono (center)
            "highpass=f=200,"              # Bass yo'qotish
            "lowpass=f=3500,"              # Yuqori chastota yo'qotish
            "equalizer=f=1000:width_type=o:width=2:g=3"  # Vocal range kuchaytirish
        ),
        "-acodec", "libmp3lame", "-b:a", "192k",
        out_mp3,
    ])
    return out_mp3 if ok else None


# ════════════════════════════════════════════════════════
#  YOUTUBE / INSTAGRAM YUKLASH
# ════════════════════════════════════════════════════════
def yt_download(url: str, quality: str, uid: int) -> str | None:
    """
    URL dan video/audio yuklab oladi.
    Muvaffaqiyatli bo'lsa fayl yo'lini qaytaradi.
    """
    import yt_dlp

    fmt_map = {
    "360":   "bestvideo[height<=360]+bestaudio/best[height<=360]/best",
    "480":   "bestvideo[height<=480]+bestaudio/best[height<=480]/best",
    "720":   "bestvideo[height<=720]+bestaudio/best[height<=720]/best",
    "1080":  "bestvideo[height<=1080]+bestaudio/best[height<=1080]/best",
    "audio": "bestaudio/best",
}
    out_tpl = _tmp(uid, f"yt_{quality}_%(id)s.%(ext)s")

    ydl_opts = {
        "format":           fmt_map.get(quality, "best"),
        "outtmpl":          out_tpl,
        "quiet":            True,
        "no_warnings":      True,
        "merge_output_format": "mp4",
        "socket_timeout":   30,
        "retries":          5,
        "fragment_retries": 5,
        "extractor_retries":3,
        "geo_bypass":       True,
        "nocheckcertificate": True,
        "http_headers": {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        },
        # Instagram uchun
        "cookiefile":       "cookies.txt" if os.path.exists("cookies.txt") else None,
    }

    # cookiefile None bo'lsa o'chirish
    if not ydl_opts["cookiefile"]:
        del ydl_opts["cookiefile"]

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if not info:
                return None
            # Yuklab olingan fayl yo'lini topish
            filename = ydl.prepare_filename(info)
    except yt_dlp.utils.DownloadError as e:
        logger.error("yt-dlp DownloadError: %s", e)
        return None
    except Exception as e:
        logger.error("yt-dlp exception: %s", e)
        return None

    # Fayl mavjudligini tekshirish (turli kengaytmalar)
    for ext in ("mp4", "webm", "mkv", "m4a", "mp3", "ogg", "opus"):
        candidate = os.path.splitext(filename)[0] + f".{ext}"
        if os.path.exists(candidate):
            return candidate

    if os.path.exists(filename):
        return filename

    # TEMP_DIR da qidirish
    uid_prefix = f"{uid}_yt_{quality}_"
    try:
        for f in os.listdir(TEMP_DIR):
            if f.startswith(str(uid)) and "yt_" in f:
                full = os.path.join(TEMP_DIR, f)
                if os.path.exists(full):
                    return full
    except OSError:
        pass

    return None


async def yt_download_async(url: str, quality: str, uid: int) -> str | None:
    """yt_download ni async wrapper."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, yt_download, url, quality, uid)


# ════════════════════════════════════════════════════════
#  TOZALASH
# ════════════════════════════════════════════════════════
def _cleanup(*paths):
    for p in paths:
        if p and os.path.exists(p):
            try:
                os.remove(p)
            except OSError:
                pass
