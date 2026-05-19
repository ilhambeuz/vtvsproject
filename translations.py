"""
🌐 VTVS Bot — Tarjimalar (UZ / RU / EN)
DB da saqlangan matnlar (to'lov, help) bu yerda emas — ular settings.py da.
"""

TEXTS = {
    "uz": {
        # ── Til tanlash ──────────────────────────────────────
        "choose_lang":      "🌐 Tilni tanlang:",
        "lang_saved":       "✅ Til saqlandi: O'zbek 🇺🇿",

        # ── Xush kelibsiz ────────────────────────────────────
        "welcome": (
            "👋 Salom, *{name}*!\n\n"
            "📤 Quyidagilarni yuboring:\n"
            "🎬 Video\n"
            "🎤 Ovozli xabar\n"
            "🎵 MP3 fayl\n"
            "🔗 YouTube / Instagram havola\n\n"
            "📊 Reja: *{plan}*\n"
            "📈 Bugungi foydalanish: *{used}/{limit}*"
        ),
        "free_plan":        "🆓 Bepul",
        "premium_plan":     "⭐ Premium",

        # ── Limit ────────────────────────────────────────────
        "limit_reached": (
            "❌ Kunlik limitga yetdingiz (*{limit}* ta).\n\n"
            "⭐ *Premium* oling — cheksiz foydalaning!"
        ),

        # ── Qayta ishlash ────────────────────────────────────
        "processing":       "⏳ Qayta ishlanmoqda...",
        "downloading":      "⬇️ Yuklanmoqda...",
        "uploading":        "📤 Yuborilmoqda...",

        # ── Fayl tanlash ─────────────────────────────────────
        "choose_action":    "✅ Yuklandi! ⏱ *{dur}*\n\nNima qilishni xohlaysiz?",
        "full_extract":     "▶️ To'liq ovoz",
        "trim_btn":         "✂️ Kesib olish",
        "speed_btn":        "🔄 Tezlik o'zgartirish",
        "vocal_btn":        "🎙 Vocal ajratish",
        "noise_btn":        "🔇 Shovqin yo'qotish",

        # ── Trim ─────────────────────────────────────────────
        "enter_start": (
            "📍 *Boshlanish vaqtini* kiriting:\n"
            "_Misol: `1:30` yoki `90` (soniya)_\n\n"
            "⏱ Davomiylik: *{dur}*"
        ),
        "enter_end": (
            "📍 *Tugash vaqtini* kiriting:\n"
            "_Misol: `3:00` yoki `180` (soniya)_\n\n"
            "⏮ Boshlanish: *{start}*"
        ),
        "bad_time":         "❌ Noto'g'ri format.\n_Misol: `1:30` yoki `90`_",
        "time_over":        "❌ Video {dur}. Kichikroq qiymat kiriting.",
        "end_before_start": "❌ Tugash vaqti boshlanishdan katta bo'lishi kerak.",

        # ── Tezlik ───────────────────────────────────────────
        "choose_speed":     "🔄 *Tezlikni tanlang:*",
        "speed_05":         "🐢 0.5x (Sekin)",
        "speed_075":        "🚶 0.75x",
        "speed_10":         "▶️ 1.0x (Normal)",
        "speed_125":        "🏃 1.25x",
        "speed_15":         "🚀 1.5x",
        "speed_20":         "⚡ 2.0x (Tez)",

        # ── Caption lar ───────────────────────────────────────
        "voice_full":       "🎤 Videodagi ovoz",
        "voice_trim":       "🎤 Kesilgan ovoz: {s} → {e}",
        "voice_speed":      "🎤 Ovoz ({speed}x tezlik)",
        "voice_vocal":      "🎙 Ajratilgan vocal",
        "voice_noise":      "🔇 Shovqin tozalangan ovoz",
        "mp3_full":         "🎵 MP3 fayl",
        "mp3_trim":         "🎵 Kesilgan MP3: {s}–{e}",
        "mp3_speed":        "🎵 MP3 ({speed}x tezlik)",
        "mp3_vocal":        "🎙 Vocal — MP3",
        "mp3_noise":        "🔇 Shovqin tozalangan MP3",

        # ── YouTube / Instagram ──────────────────────────────
        "choose_quality":   "🎬 Sifatni tanlang:\n_(Bepul: 360p yoki Ovoz)_",
        "choose_quality_p": "🎬 Sifatni tanlang:",
        "q_360":            "📱 360p",
        "q_480":            "💻 480p",
        "q_720":            "🖥 720p HD",
        "q_1080":           "🎬 1080p FHD",
        "q_audio":          "🎵 Faqat ovoz",
        "free_quality_only":"❌ Bepul foydalanuvchilar faqat 360p va ovoz olishi mumkin.\n\n⭐ Premium oling!",
        "yt_too_big":       "⚠️ Fayl {size} MB — Telegram 50 MB qabul qiladi.\nKichikroq sifat tanlang.",

        # ── Premium ───────────────────────────────────────────
        "already_premium":  "⭐ Sizda allaqachon Premium faol!\n📅 *{until}* gacha",
        "stars_invoice_title": "⭐ VTVS Premium",
        "stars_invoice_desc":  "30 kunlik Premium obuna — cheksiz imkoniyatlar!",
        "stars_success": (
            "🎉 *To'lov qabul qilindi!*\n\n"
            "⭐ *{days} kunlik Premium* faollashtirildi!\n"
            "📅 *{until}* gacha\n\n"
            "✂️ Endi istalgan videoni kesib oling!"
        ),
        "pay_confirmed": (
            "🎉 *Tabriklaymiz!*\n\n"
            "✅ To'lovingiz tasdiqlandi!\n"
            "⭐ *{days} kunlik Premium* faollashtirildi!\n"
            "📅 *{until}* gacha"
        ),
        "pay_rejected": (
            "❌ *To'lovingiz tasdiqlanmadi.*\n\n"
            "Muammo bo'lsa to'lov ma'lumotlarini tekshiring."
        ),
        "i_paid":           "✅ To'lov qildim",
        "pay_stars":        "⭐ Telegram Stars bilan",
        "get_premium":      "⭐ Premium olish",
        "send_screenshot":  "📸 To'lov chekining *screenshotini* yuboring:",
        "screenshot_sent":  "✅ Screenshot yuborildi!\n⏳ Admin tekshirmoqda...",

        # ── Promo kod ─────────────────────────────────────────
        "enter_promo":      "🎟 *Promo-kodni* kiriting:",
        "promo_btn":        "🎟 Promo-kod",
        "promo_ok":         "✅ Promo-kod qabul qilindi!\n🎁 *+{days} kun* Premium qo'shildi!",
        "promo_invalid":    "❌ Promo-kod noto'g'ri yoki muddati o'tgan.",
        "promo_used":       "❌ Bu promo-kodni siz allaqachon ishlatgansiz.",

        # ── Referal ───────────────────────────────────────────
        "ref_info": (
            "👥 *Referal dasturi*\n\n"
            "Har bir taklif qilgan do'stingiz uchun *+{bonus} kun* bonus!\n\n"
            "🔗 Sizning havolangiz:\n`{link}`\n\n"
            "✅ Taklif qilganlar: *{count}* ta\n"
            "🎁 Jami bonus kunlar: *{days}* kun"
        ),
        "ref_bonus_received": (
            "🎁 *{name}* sizning havolangiz orqali qo'shildi!\n"
            "⭐ *+{bonus} kun* Premium bonus qo'shildi!"
        ),
        "ref_bonus_note": (
            "ℹ️ Bonus kunlar Premium obunangizga qo'shiladi.\n"
            "Hozirda Premium yo'q bo'lsa, bonus kunlar keyingi obunangizdan qo'shiladi."
        ),

        # ── Premium tugash ogohlantiruvi ──────────────────────
        "premium_expiring": (
            "⚠️ *Diqqat!*\n\n"
            "Sizning Premium obunangiz *{days} kun* ichida tugaydi.\n"
            "📅 Tugash sanasi: *{until}*\n\n"
            "Uzluksiz foydalanish uchun yangilang 👇"
        ),

        # ── Foydalanuvchi statistikasi ────────────────────────
        "my_stats": (
            "📊 *Sizning statistikangiz:*\n\n"
            "👤 Ism: *{name}*\n"
            "🎯 Reja: *{plan}*\n"
            "📅 Premium: *{until}*\n"
            "📈 Bugungi foydalanish: *{used}/{limit}*\n"
            "📦 Jami qayta ishlangan: *{total}* ta\n"
            "👥 Taklif qilganlar: *{refs}* ta\n"
            "📅 Ro'yxatdan: *{since}*"
        ),
        "prem_until":       "{date} gacha",
        "no_premium":       "Yo'q",

        # ── Til tugmasi ───────────────────────────────────────
        "change_lang":      "🌐 Tilni o'zgartirish",

        # ── Boshqa ───────────────────────────────────────────
        "banned":           "🚫 Siz botdan foydalana olmaysiz.",
        "error":            "❌ Xatolik yuz berdi. Qaytadan urinib ko'ring.",
        "no_file":          "❌ Fayl topilmadi. Qaytadan yuboring.",
        "hint": (
            "📤 Yuboring:\n"
            "🎬 Video | 🎤 Ovozli xabar | 🎵 MP3\n"
            "🔗 YouTube / Instagram havola\n\n"
            "/premium | /referral | /stats | /help"
        ),
        "back":             "◀️ Orqaga",
        "cancel":           "❌ Bekor",
        "my_status_btn":    "📊 Statusim",
        "ref_btn":          "👥 Referal",
        "stats_btn":        "📈 Statistikam",
    },

    "ru": {
        "choose_lang":      "🌐 Выберите язык:",
        "lang_saved":       "✅ Язык сохранён: Русский 🇷🇺",
        "welcome": (
            "👋 Привет, *{name}*!\n\n"
            "📤 Отправьте:\n"
            "🎬 Видео\n"
            "🎤 Голосовое сообщение\n"
            "🎵 MP3 файл\n"
            "🔗 Ссылку YouTube / Instagram\n\n"
            "📊 Тариф: *{plan}*\n"
            "📈 Использований сегодня: *{used}/{limit}*"
        ),
        "free_plan":        "🆓 Бесплатный",
        "premium_plan":     "⭐ Премиум",
        "limit_reached": (
            "❌ Дневной лимит исчерпан (*{limit}*).\n\n"
            "⭐ Оформите *Премиум* — без ограничений!"
        ),
        "processing":       "⏳ Обрабатывается...",
        "downloading":      "⬇️ Загрузка...",
        "uploading":        "📤 Отправляется...",
        "choose_action":    "✅ Загружено! ⏱ *{dur}*\n\nЧто хотите сделать?",
        "full_extract":     "▶️ Полный звук",
        "trim_btn":         "✂️ Обрезать",
        "speed_btn":        "🔄 Изменить скорость",
        "vocal_btn":        "🎙 Выделить вокал",
        "noise_btn":        "🔇 Убрать шум",
        "enter_start": (
            "📍 *Введите время начала*:\n"
            "_Пример: `1:30` или `90` (секунд)_\n\n"
            "⏱ Длительность: *{dur}*"
        ),
        "enter_end": (
            "📍 *Введите время конца*:\n"
            "_Пример: `3:00` или `180` (секунд)_\n\n"
            "⏮ Начало: *{start}*"
        ),
        "bad_time":         "❌ Неверный формат.\n_Пример: `1:30` или `90`_",
        "time_over":        "❌ Видео {dur}. Введите меньшее значение.",
        "end_before_start": "❌ Конец должен быть больше начала.",
        "choose_speed":     "🔄 *Выберите скорость:*",
        "speed_05":         "🐢 0.5x (Медленно)",
        "speed_075":        "🚶 0.75x",
        "speed_10":         "▶️ 1.0x (Нормально)",
        "speed_125":        "🏃 1.25x",
        "speed_15":         "🚀 1.5x",
        "speed_20":         "⚡ 2.0x (Быстро)",
        "voice_full":       "🎤 Звук из видео",
        "voice_trim":       "🎤 Обрезанный звук: {s} → {e}",
        "voice_speed":      "🎤 Звук ({speed}x скорость)",
        "voice_vocal":      "🎙 Выделенный вокал",
        "voice_noise":      "🔇 Очищенный от шума звук",
        "mp3_full":         "🎵 MP3 файл",
        "mp3_trim":         "🎵 Обрезанный MP3: {s}–{e}",
        "mp3_speed":        "🎵 MP3 ({speed}x скорость)",
        "mp3_vocal":        "🎙 Вокал — MP3",
        "mp3_noise":        "🔇 Очищенный MP3",
        "choose_quality":   "🎬 Выберите качество:\n_(Бесплатно: 360p или Аудио)_",
        "choose_quality_p": "🎬 Выберите качество:",
        "q_360":            "📱 360p",
        "q_480":            "💻 480p",
        "q_720":            "🖥 720p HD",
        "q_1080":           "🎬 1080p FHD",
        "q_audio":          "🎵 Только аудио",
        "free_quality_only":"❌ Бесплатные пользователи: только 360p и аудио.\n\n⭐ Оформите Премиум!",
        "yt_too_big":       "⚠️ Файл {size} МБ — Telegram принимает до 50 МБ.\nВыберите меньшее качество.",
        "already_premium":  "⭐ У вас уже активен Премиум!\n📅 До *{until}*",
        "stars_invoice_title": "⭐ VTVS Премиум",
        "stars_invoice_desc":  "30-дневная Премиум подписка — безлимитные возможности!",
        "stars_success": (
            "🎉 *Оплата получена!*\n\n"
            "⭐ *Премиум на {days} дней* активирован!\n"
            "📅 До *{until}*"
        ),
        "pay_confirmed": (
            "🎉 *Поздравляем!*\n\n"
            "✅ Оплата подтверждена!\n"
            "⭐ *Премиум на {days} дней* активирован!\n"
            "📅 До *{until}*"
        ),
        "pay_rejected": (
            "❌ *Оплата не подтверждена.*\n\n"
            "Проверьте данные оплаты и попробуйте снова."
        ),
        "i_paid":           "✅ Я оплатил",
        "pay_stars":        "⭐ Telegram Stars",
        "get_premium":      "⭐ Получить Премиум",
        "send_screenshot":  "📸 Отправьте *скриншот* чека оплаты:",
        "screenshot_sent":  "✅ Скриншот отправлен!\n⏳ Проверяется администратором...",
        "enter_promo":      "🎟 Введите *промо-код*:",
        "promo_btn":        "🎟 Промо-код",
        "promo_ok":         "✅ Промо-код принят!\n🎁 *+{days} дней* Премиум добавлено!",
        "promo_invalid":    "❌ Промо-код неверный или просрочен.",
        "promo_used":       "❌ Вы уже использовали этот промо-код.",
        "ref_info": (
            "👥 *Реферальная программа*\n\n"
            "За каждого приглашённого *+{bonus} дней* бонуса!\n\n"
            "🔗 Ваша ссылка:\n`{link}`\n\n"
            "✅ Приглашено: *{count}*\n"
            "🎁 Бонусных дней: *{days}*"
        ),
        "ref_bonus_received": (
            "🎁 *{name}* присоединился по вашей ссылке!\n"
            "⭐ *+{bonus} дней* Премиум бонуса!"
        ),
        "ref_bonus_note": (
            "ℹ️ Бонусные дни добавляются к вашей Premium подписке.\n"
            "Если Премиум не активен — дни добавятся к следующей подписке."
        ),
        "premium_expiring": (
            "⚠️ *Внимание!*\n\n"
            "Ваш Премиум заканчивается через *{days} дн.*\n"
            "📅 Дата окончания: *{until}*\n\n"
            "Продлите для непрерывного использования 👇"
        ),
        "my_stats": (
            "📊 *Ваша статистика:*\n\n"
            "👤 Имя: *{name}*\n"
            "🎯 Тариф: *{plan}*\n"
            "📅 Премиум: *{until}*\n"
            "📈 Сегодня: *{used}/{limit}*\n"
            "📦 Обработано всего: *{total}*\n"
            "👥 Приглашено: *{refs}*\n"
            "📅 Зарегистрирован: *{since}*"
        ),
        "prem_until":       "до {date}",
        "no_premium":       "Нет",
        "change_lang":      "🌐 Сменить язык",
        "banned":           "🚫 Вы не можете использовать бота.",
        "error":            "❌ Произошла ошибка. Попробуйте снова.",
        "no_file":          "❌ Файл не найден. Отправьте снова.",
        "hint": (
            "📤 Отправьте:\n"
            "🎬 Видео | 🎤 Голосовое | 🎵 MP3\n"
            "🔗 YouTube / Instagram\n\n"
            "/premium | /referral | /stats | /help"
        ),
        "back":             "◀️ Назад",
        "cancel":           "❌ Отмена",
        "my_status_btn":    "📊 Мой статус",
        "ref_btn":          "👥 Реферал",
        "stats_btn":        "📈 Моя статистика",
    },

    "en": {
        "choose_lang":      "🌐 Choose language:",
        "lang_saved":       "✅ Language saved: English 🇬🇧",
        "welcome": (
            "👋 Hello, *{name}*!\n\n"
            "📤 Send me:\n"
            "🎬 Video\n"
            "🎤 Voice message\n"
            "🎵 MP3 file\n"
            "🔗 YouTube / Instagram link\n\n"
            "📊 Plan: *{plan}*\n"
            "📈 Today's usage: *{used}/{limit}*"
        ),
        "free_plan":        "🆓 Free",
        "premium_plan":     "⭐ Premium",
        "limit_reached": (
            "❌ Daily limit reached (*{limit}*).\n\n"
            "⭐ Get *Premium* — unlimited usage!"
        ),
        "processing":       "⏳ Processing...",
        "downloading":      "⬇️ Downloading...",
        "uploading":        "📤 Uploading...",
        "choose_action":    "✅ Loaded! ⏱ *{dur}*\n\nWhat would you like to do?",
        "full_extract":     "▶️ Full audio",
        "trim_btn":         "✂️ Trim audio",
        "speed_btn":        "🔄 Change speed",
        "vocal_btn":        "🎙 Isolate vocals",
        "noise_btn":        "🔇 Remove noise",
        "enter_start": (
            "📍 *Enter start time*:\n"
            "_Example: `1:30` or `90` (seconds)_\n\n"
            "⏱ Duration: *{dur}*"
        ),
        "enter_end": (
            "📍 *Enter end time*:\n"
            "_Example: `3:00` or `180` (seconds)_\n\n"
            "⏮ Start: *{start}*"
        ),
        "bad_time":         "❌ Invalid format.\n_Example: `1:30` or `90`_",
        "time_over":        "❌ Video is {dur}. Enter a smaller value.",
        "end_before_start": "❌ End time must be greater than start.",
        "choose_speed":     "🔄 *Choose speed:*",
        "speed_05":         "🐢 0.5x (Slow)",
        "speed_075":        "🚶 0.75x",
        "speed_10":         "▶️ 1.0x (Normal)",
        "speed_125":        "🏃 1.25x",
        "speed_15":         "🚀 1.5x",
        "speed_20":         "⚡ 2.0x (Fast)",
        "voice_full":       "🎤 Audio from video",
        "voice_trim":       "🎤 Trimmed audio: {s} → {e}",
        "voice_speed":      "🎤 Audio ({speed}x speed)",
        "voice_vocal":      "🎙 Isolated vocals",
        "voice_noise":      "🔇 Noise-cleaned audio",
        "mp3_full":         "🎵 MP3 file",
        "mp3_trim":         "🎵 Trimmed MP3: {s}–{e}",
        "mp3_speed":        "🎵 MP3 ({speed}x speed)",
        "mp3_vocal":        "🎙 Vocals — MP3",
        "mp3_noise":        "🔇 Noise-cleaned MP3",
        "choose_quality":   "🎬 Choose quality:\n_(Free: 360p or Audio)_",
        "choose_quality_p": "🎬 Choose quality:",
        "q_360":            "📱 360p",
        "q_480":            "💻 480p",
        "q_720":            "🖥 720p HD",
        "q_1080":           "🎬 1080p FHD",
        "q_audio":          "🎵 Audio only",
        "free_quality_only":"❌ Free users: only 360p and audio.\n\n⭐ Get Premium!",
        "yt_too_big":       "⚠️ File is {size} MB — Telegram accepts up to 50 MB.\nChoose lower quality.",
        "already_premium":  "⭐ You already have active Premium!\n📅 Until *{until}*",
        "stars_invoice_title": "⭐ VTVS Premium",
        "stars_invoice_desc":  "30-day Premium subscription — unlimited features!",
        "stars_success": (
            "🎉 *Payment received!*\n\n"
            "⭐ *{days}-day Premium* activated!\n"
            "📅 Until *{until}*"
        ),
        "pay_confirmed": (
            "🎉 *Congratulations!*\n\n"
            "✅ Payment confirmed!\n"
            "⭐ *{days}-day Premium* activated!\n"
            "📅 Until *{until}*"
        ),
        "pay_rejected": (
            "❌ *Payment not confirmed.*\n\n"
            "Please check payment details and try again."
        ),
        "i_paid":           "✅ I paid",
        "pay_stars":        "⭐ Pay with Stars",
        "get_premium":      "⭐ Get Premium",
        "send_screenshot":  "📸 Send *screenshot* of your payment receipt:",
        "screenshot_sent":  "✅ Screenshot sent!\n⏳ Being reviewed by admin...",
        "enter_promo":      "🎟 Enter *promo code*:",
        "promo_btn":        "🎟 Promo code",
        "promo_ok":         "✅ Promo code accepted!\n🎁 *+{days} days* Premium added!",
        "promo_invalid":    "❌ Invalid or expired promo code.",
        "promo_used":       "❌ You have already used this promo code.",
        "ref_info": (
            "👥 *Referral Program*\n\n"
            "Get *+{bonus} days* for each friend you invite!\n\n"
            "🔗 Your link:\n`{link}`\n\n"
            "✅ Referred: *{count}*\n"
            "🎁 Bonus days: *{days}*"
        ),
        "ref_bonus_received": (
            "🎁 *{name}* joined via your link!\n"
            "⭐ *+{bonus} days* Premium bonus added!"
        ),
        "ref_bonus_note": (
            "ℹ️ Bonus days are added to your Premium subscription.\n"
            "If no active Premium — days added to your next subscription."
        ),
        "premium_expiring": (
            "⚠️ *Attention!*\n\n"
            "Your Premium expires in *{days} days*.\n"
            "📅 Expiry: *{until}*\n\n"
            "Renew to continue uninterrupted 👇"
        ),
        "my_stats": (
            "📊 *Your statistics:*\n\n"
            "👤 Name: *{name}*\n"
            "🎯 Plan: *{plan}*\n"
            "📅 Premium: *{until}*\n"
            "📈 Today: *{used}/{limit}*\n"
            "📦 Total processed: *{total}*\n"
            "👥 Referred: *{refs}*\n"
            "📅 Joined: *{since}*"
        ),
        "prem_until":       "until {date}",
        "no_premium":       "None",
        "change_lang":      "🌐 Change language",
        "banned":           "🚫 You are banned from using this bot.",
        "error":            "❌ An error occurred. Please try again.",
        "no_file":          "❌ File not found. Please send again.",
        "hint": (
            "📤 Send me:\n"
            "🎬 Video | 🎤 Voice | 🎵 MP3\n"
            "🔗 YouTube / Instagram\n\n"
            "/premium | /referral | /stats | /help"
        ),
        "back":             "◀️ Back",
        "cancel":           "❌ Cancel",
        "my_status_btn":    "📊 My status",
        "ref_btn":          "👥 Referral",
        "stats_btn":        "📈 My stats",
    },
}


def tx(lang_or_uid, key: str, **kw) -> str:
    """Tarjima olish. lang_or_uid = 'uz'|'ru'|'en' yoki user_id (int)."""
    from database import get_lang  # circular import oldini olish
    if isinstance(lang_or_uid, int):
        lang = get_lang(lang_or_uid)
    else:
        lang = lang_or_uid if lang_or_uid in TEXTS else "en"
    text = TEXTS.get(lang, TEXTS["en"]).get(key, TEXTS["en"].get(key, key))
    return text.format(**kw) if kw else text
