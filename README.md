# 🎬 VTVS Bot v4.0

## Fayl tuzilmasi
```
vtvs_bot/
├── config.py        ← Faqat shu faylni o'zgartiring
├── translations.py  ← Barcha matnlar (UZ/RU/EN)
├── database.py      ← Database
├── audio.py         ← ffmpeg + yt-dlp
├── keyboards.py     ← Tugmalar
├── admin.py         ← Admin panel
├── broadcast.py     ← Xabar yuborish
├── scheduler.py     ← Avtomatik vazifalar
├── bot.py           ← Asosiy fayl (ishga tushirish)
└── requirements.txt
```

## O'rnatish

```bash
# 1. Kutubxonalar
pip install -r requirements.txt

# 2. ffmpeg
sudo apt install ffmpeg          # Ubuntu/Debian
brew install ffmpeg              # Mac

# 3. config.py ni o'zgartirish
nano config.py
# BOT_TOKEN, BOT_USERNAME, ADMIN_IDS ni o'zgartiring

# 4. Ishga tushirish
python bot.py
```

## config.py sozlamalari

| Sozlama | Ma'no |
|---|---|
| `BOT_TOKEN` | BotFather dan olingan token |
| `BOT_USERNAME` | Botning @ username (@ siz) |
| `ADMIN_IDS` | Admin Telegram ID lari ro'yxati |
| `PREMIUM_DAYS` | Premium necha kun (default: 30) |
| `PREMIUM_PRICE` | Ko'rsatiladigan narx (default: $3) |
| `STARS_AMOUNT` | Telegram Stars narxi (default: 150) |
| `FREE_DAILY_LIMIT` | Kunlik bepul limit (default: 5) |
| `USE_DEMUCS` | True = sifatli vocal (demucs kerak) |

## Instagram uchun (ixtiyoriy)

Instagram yuklash uchun cookies.txt kerak bo'lishi mumkin.
Bot bilan bir papkada `cookies.txt` fayl qo'ying.
Cookies ni browser extension orqali olish mumkin: "Get cookies.txt"

## Admin ID ni bilish

@userinfobot ga /start yuboring → ID chiqadi.

## PythonAnywhere uchun

```bash
git clone https://github.com/sizning_repo
cd vtvs_bot
pip install -r requirements.txt --user
python bot.py
```

## Vocal isolation (demucs)

Yuqori sifatli vocal ajratish uchun:
```bash
pip install demucs
```
Keyin config.py da: `USE_DEMUCS = True`

⚠️ demucs juda ko'p RAM va vaqt talab qiladi.
PythonAnywhere free tier da ishlamasligi mumkin.
