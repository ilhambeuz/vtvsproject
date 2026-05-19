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
            "👋 Salom, <b>{name}</b>!\n\n"
            "📤 Quyidagilarni yuboring:\n"
            "🎬 Video\n"
            "🎤 Ovozli xabar\n"
            "🎵 MP3 fayl\n"
            "🔗 YouTube / Instagram havola\n\n"
            "📊 Reja: <b>{plan}</b>\n"
            "📈 Bugungi foydalanish: <b>{used}/{limit}</b>"
        ),
        "free_plan":        "🆓 Bepul",
        "premium_plan":     "⭐ Premium",

        # ── Limit ────────────────────────────────────────────
        "limit_reached": (
            "❌ Kunlik limitga yetdingiz (<b>{limit}</b> ta).\n\n"
            "⭐ <b>Premium</b> oling — cheksiz foydalaning!"
        ),

        # ── Qayta ishlash ────────────────────────────────────
        "processing":       "⏳ Qayta ishlanmoqda...",
        "downloading":      "⬇️ Yuklanmoqda...",
        "uploading":        "📤 Yuborilmoqda...",

        # ── Fayl tanlash ─────────────────────────────────────
        "choose_action":    "✅ Yuklandi! ⏱ <b>{dur}</b>\n\nNima qilishni xohlaysiz?",
        "full_extract":     "▶️ To'liq ovoz",
        "trim_btn":         "✂️ Kesib olish",
        "speed_btn":        "🔄 Tezlik o'zgartirish",
        "vocal_btn":        "🎙 Vocal ajratish",
        "noise_btn":        "🔇 Shovqin yo'qotish",

        # ── Trim ─────────────────────────────────────────────
        "enter_start": (
            "📍 <b>Boshlanish vaqtini</b> kiriting:\n"
            "_Misol: <code>1:30</code> yoki <code>90</code> (soniya)_\n\n"
            "⏱ Davomiylik: <b>{dur}</b>"
        ),
        "enter_end": (
            "📍 <b>Tugash vaqtini</b> kiriting:\n"
            "_Misol: <code>3:00</code> yoki <code>180</code> (soniya)_\n\n"
            "⏮ Boshlanish: <b>{start}</b>"
        ),
        "bad_time":         "❌ Noto'g'ri format.\n_Misol: <code>1:30</code> yoki <code>90</code>_",
        "time_over":        "❌ Video {dur}. Kichikroq qiymat kiriting.",
        "end_before_start": "❌ Tugash vaqti boshlanishdan katta bo'lishi kerak.",

        # ── Tezlik ───────────────────────────────────────────
        "choose_speed":     "🔄 <b>Tezlikni tanlang:</b>",
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
        "already_premium":  "⭐ Sizda allaqachon Premium faol!\n📅 <b>{until}</b> gacha",
        "stars_invoice_title": "⭐ VTVS Premium",
        "stars_invoice_desc":  "30 kunlik Premium obuna — cheksiz imkoniyatlar!",
        "stars_success": (
            "🎉 <b>To'lov qabul qilindi!</b>\n\n"
            "⭐ <b>{days} kunlik Premium</b> faollashtirildi!\n"
            "📅 <b>{until}</b> gacha\n\n"
            "✂️ Endi istalgan videoni kesib oling!"
        ),
        "pay_confirmed": (
            "🎉 <b>Tabriklaymiz!</b>\n\n"
            "✅ To'lovingiz tasdiqlandi!\n"
            "⭐ <b>{days} kunlik Premium</b> faollashtirildi!\n"
            "📅 <b>{until}</b> gacha"
        ),
        "pay_rejected": (
            "❌ <b>To'lovingiz tasdiqlanmadi.</b>\n\n"
            "Muammo bo'lsa to'lov ma'lumotlarini tekshiring."
        ),
        "i_paid":           "✅ To'lov qildim",
        "pay_stars":        "⭐ Telegram Stars bilan",
        "get_premium":      "⭐ Premium olish",
        "send_screenshot":  "📸 To'lov chekining <b>screenshotini</b> yuboring:",
        "screenshot_sent":  "✅ Screenshot yuborildi!\n⏳ Admin tekshirmoqda...",

        # ── Promo kod ─────────────────────────────────────────
        "enter_promo":      "🎟 <b>Promo-kodni</b> kiriting:",
        "promo_btn":        "🎟 Promo-kod",
        "promo_ok":         "✅ Promo-kod qabul qilindi!\n🎁 <b>+{days} kun</b> Premium qo'shildi!",
        "promo_invalid":    "❌ Promo-kod noto'g'ri yoki muddati o'tgan.",
        "promo_used":       "❌ Bu promo-kodni siz allaqachon ishlatgansiz.",

        # ── Referal ───────────────────────────────────────────
        "ref_info": (
            "👥 <b>Referal dasturi</b>\n\n"
            "Har bir taklif qilgan do'stingiz uchun <b>+{bonus} kun</b> bonus!\n\n"
            "🔗 Sizning havolangiz:\n<code>{link}</code>\n\n"
            "✅ Taklif qilganlar: <b>{count}</b> ta\n"
            "🎁 Jami bonus kunlar: <b>{days}</b> kun"
        ),
        "ref_bonus_received": (
            "🎁 <b>{name}</b> sizning havolangiz orqali qo'shildi!\n"
            "⭐ <b>+{bonus} kun</b> Premium bonus qo'shildi!"
        ),
        "ref_bonus_note": (
            "ℹ️ Bonus kunlar Premium obunangizga qo'shiladi.\n"
            "Hozirda Premium yo'q bo'lsa, bonus kunlar keyingi obunangizdan qo'shiladi."
        ),

        # ── Premium tugash ogohlantiruvi ──────────────────────
        "premium_expiring": (
            "⚠️ <b>Diqqat!</b>\n\n"
            "Sizning Premium obunangiz <b>{days} kun</b> ichida tugaydi.\n"
            "📅 Tugash sanasi: <b>{until}</b>\n\n"
            "Uzluksiz foydalanish uchun yangilang 👇"
        ),

        # ── Foydalanuvchi statistikasi ────────────────────────
        "my_stats": (
            "📊 <b>Sizning statistikangiz:</b>\n\n"
            "👤 Ism: <b>{name}</b>\n"
            "🎯 Reja: <b>{plan}</b>\n"
            "📅 Premium: <b>{until}</b>\n"
            "📈 Bugungi foydalanish: <b>{used}/{limit}</b>\n"
            "📦 Jami qayta ishlangan: <b>{total}</b> ta\n"
            "👥 Taklif qilganlar: <b>{refs}</b> ta\n"
            "📅 Ro'yxatdan: <b>{since}</b>"
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
            "👋 Привет, <b>{name}</b>!\n\n"
            "📤 Отправьте:\n"
            "🎬 Видео\n"
            "🎤 Голосовое сообщение\n"
            "🎵 MP3 файл\n"
            "🔗 Ссылку YouTube / Instagram\n\n"
            "📊 Тариф: <b>{plan}</b>\n"
            "📈 Использований сегодня: <b>{used}/{limit}</b>"
        ),
        "free_plan":        "🆓 Бесплатный",
        "premium_plan":     "⭐ Премиум",
        "limit_reached": (
            "❌ Дневной лимит исчерпан (<b>{limit}</b>).\n\n"
            "⭐ Оформите <b>Премиум</b> — без ограничений!"
        ),
        "processing":       "⏳ Обрабатывается...",
        "downloading":      "⬇️ Загрузка...",
        "uploading":        "📤 Отправляется...",
        "choose_action":    "✅ Загружено! ⏱ <b>{dur}</b>\n\nЧто хотите сделать?",
        "full_extract":     "▶️ Полный звук",
        "trim_btn":         "✂️ Обрезать",
        "speed_btn":        "🔄 Изменить скорость",
        "vocal_btn":        "🎙 Выделить вокал",
        "noise_btn":        "🔇 Убрать шум",
        "enter_start": (
            "📍 <b>Введите время начала</b>:\n"
            "_Пример: <code>1:30</code> или <code>90</code> (секунд)_\n\n"
            "⏱ Длительность: <b>{dur}</b>"
        ),
        "enter_end": (
            "📍 <b>Введите время конца</b>:\n"
            "_Пример: <code>3:00</code> или <code>180</code> (секунд)_\n\n"
            "⏮ Начало: <b>{start}</b>"
        ),
        "bad_time":         "❌ Неверный формат.\n_Пример: <code>1:30</code> или <code>90</code>_",
        "time_over":        "❌ Видео {dur}. Введите меньшее значение.",
        "end_before_start": "❌ Конец должен быть больше начала.",
        "choose_speed":     "🔄 <b>Выберите скорость:</b>",
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
        "already_premium":  "⭐ У вас уже активен Премиум!\n📅 До <b>{until}</b>",
        "stars_invoice_title": "⭐ VTVS Премиум",
        "stars_invoice_desc":  "30-дневная Премиум подписка — безлимитные возможности!",
        "stars_success": (
            "🎉 <b>Оплата получена!</b>\n\n"
            "⭐ <b>Премиум на {days} дней</b> активирован!\n"
            "📅 До <b>{until}</b>"
        ),
        "pay_confirmed": (
            "🎉 <b>Поздравляем!</b>\n\n"
            "✅ Оплата подтверждена!\n"
            "⭐ <b>Премиум на {days} дней</b> активирован!\n"
            "📅 До <b>{until}</b>"
        ),
        "pay_rejected": (
            "❌ <b>Оплата не подтверждена.</b>\n\n"
            "Проверьте данные оплаты и попробуйте снова."
        ),
        "i_paid":           "✅ Я оплатил",
        "pay_stars":        "⭐ Telegram Stars",
        "get_premium":      "⭐ Получить Премиум",
        "send_screenshot":  "📸 Отправьте <b>скриншот</b> чека оплаты:",
        "screenshot_sent":  "✅ Скриншот отправлен!\n⏳ Проверяется администратором...",
        "enter_promo":      "🎟 Введите <b>промо-код</b>:",
        "promo_btn":        "🎟 Промо-код",
        "promo_ok":         "✅ Промо-код принят!\n🎁 <b>+{days} дней</b> Премиум добавлено!",
        "promo_invalid":    "❌ Промо-код неверный или просрочен.",
        "promo_used":       "❌ Вы уже использовали этот промо-код.",
        "ref_info": (
            "👥 <b>Реферальная программа</b>\n\n"
            "За каждого приглашённого <b>+{bonus} дней</b> бонуса!\n\n"
            "🔗 Ваша ссылка:\n<code>{link}</code>\n\n"
            "✅ Приглашено: <b>{count}</b>\n"
            "🎁 Бонусных дней: <b>{days}</b>"
        ),
        "ref_bonus_received": (
            "🎁 <b>{name}</b> присоединился по вашей ссылке!\n"
            "⭐ <b>+{bonus} дней</b> Премиум бонуса!"
        ),
        "ref_bonus_note": (
            "ℹ️ Бонусные дни добавляются к вашей Premium подписке.\n"
            "Если Премиум не активен — дни добавятся к следующей подписке."
        ),
        "premium_expiring": (
            "⚠️ <b>Внимание!</b>\n\n"
            "Ваш Премиум заканчивается через <b>{days} дн.</b>\n"
            "📅 Дата окончания: <b>{until}</b>\n\n"
            "Продлите для непрерывного использования 👇"
        ),
        "my_stats": (
            "📊 <b>Ваша статистика:</b>\n\n"
            "👤 Имя: <b>{name}</b>\n"
            "🎯 Тариф: <b>{plan}</b>\n"
            "📅 Премиум: <b>{until}</b>\n"
            "📈 Сегодня: <b>{used}/{limit}</b>\n"
            "📦 Обработано всего: <b>{total}</b>\n"
            "👥 Приглашено: <b>{refs}</b>\n"
            "📅 Зарегистрирован: <b>{since}</b>"
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
            "👋 Hello, <b>{name}</b>!\n\n"
            "📤 Send me:\n"
            "🎬 Video\n"
            "🎤 Voice message\n"
            "🎵 MP3 file\n"
            "🔗 YouTube / Instagram link\n\n"
            "📊 Plan: <b>{plan}</b>\n"
            "📈 Today's usage: <b>{used}/{limit}</b>"
        ),
        "free_plan":        "🆓 Free",
        "premium_plan":     "⭐ Premium",
        "limit_reached": (
            "❌ Daily limit reached (<b>{limit}</b>).\n\n"
            "⭐ Get <b>Premium</b> — unlimited usage!"
        ),
        "processing":       "⏳ Processing...",
        "downloading":      "⬇️ Downloading...",
        "uploading":        "📤 Uploading...",
        "choose_action":    "✅ Loaded! ⏱ <b>{dur}</b>\n\nWhat would you like to do?",
        "full_extract":     "▶️ Full audio",
        "trim_btn":         "✂️ Trim audio",
        "speed_btn":        "🔄 Change speed",
        "vocal_btn":        "🎙 Isolate vocals",
        "noise_btn":        "🔇 Remove noise",
        "enter_start": (
            "📍 <b>Enter start time</b>:\n"
            "_Example: <code>1:30</code> or <code>90</code> (seconds)_\n\n"
            "⏱ Duration: <b>{dur}</b>"
        ),
        "enter_end": (
            "📍 <b>Enter end time</b>:\n"
            "_Example: <code>3:00</code> or <code>180</code> (seconds)_\n\n"
            "⏮ Start: <b>{start}</b>"
        ),
        "bad_time":         "❌ Invalid format.\n_Example: <code>1:30</code> or <code>90</code>_",
        "time_over":        "❌ Video is {dur}. Enter a smaller value.",
        "end_before_start": "❌ End time must be greater than start.",
        "choose_speed":     "🔄 <b>Choose speed:</b>",
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
        "already_premium":  "⭐ You already have active Premium!\n📅 Until <b>{until}</b>",
        "stars_invoice_title": "⭐ VTVS Premium",
        "stars_invoice_desc":  "30-day Premium subscription — unlimited features!",
        "stars_success": (
            "🎉 <b>Payment received!</b>\n\n"
            "⭐ <b>{days}-day Premium</b> activated!\n"
            "📅 Until <b>{until}</b>"
        ),
        "pay_confirmed": (
            "🎉 <b>Congratulations!</b>\n\n"
            "✅ Payment confirmed!\n"
            "⭐ <b>{days}-day Premium</b> activated!\n"
            "📅 Until <b>{until}</b>"
        ),
        "pay_rejected": (
            "❌ <b>Payment not confirmed.</b>\n\n"
            "Please check payment details and try again."
        ),
        "i_paid":           "✅ I paid",
        "pay_stars":        "⭐ Pay with Stars",
        "get_premium":      "⭐ Get Premium",
        "send_screenshot":  "📸 Send <b>screenshot</b> of your payment receipt:",
        "screenshot_sent":  "✅ Screenshot sent!\n⏳ Being reviewed by admin...",
        "enter_promo":      "🎟 Enter <b>promo code</b>:",
        "promo_btn":        "🎟 Promo code",
        "promo_ok":         "✅ Promo code accepted!\n🎁 <b>+{days} days</b> Premium added!",
        "promo_invalid":    "❌ Invalid or expired promo code.",
        "promo_used":       "❌ You have already used this promo code.",
        "ref_info": (
            "👥 <b>Referral Program</b>\n\n"
            "Get <b>+{bonus} days</b> for each friend you invite!\n\n"
            "🔗 Your link:\n<code>{link}</code>\n\n"
            "✅ Referred: <b>{count}</b>\n"
            "🎁 Bonus days: <b>{days}</b>"
        ),
        "ref_bonus_received": (
            "🎁 <b>{name}</b> joined via your link!\n"
            "⭐ <b>+{bonus} days</b> Premium bonus added!"
        ),
        "ref_bonus_note": (
            "ℹ️ Bonus days are added to your Premium subscription.\n"
            "If no active Premium — days added to your next subscription."
        ),
        "premium_expiring": (
            "⚠️ <b>Attention!</b>\n\n"
            "Your Premium expires in <b>{days} days</b>.\n"
            "📅 Expiry: <b>{until}</b>\n\n"
            "Renew to continue uninterrupted 👇"
        ),
        "my_stats": (
            "📊 <b>Your statistics:</b>\n\n"
            "👤 Name: <b>{name}</b>\n"
            "🎯 Plan: <b>{plan}</b>\n"
            "📅 Premium: <b>{until}</b>\n"
            "📈 Today: <b>{used}/{limit}</b>\n"
            "📦 Total processed: <b>{total}</b>\n"
            "👥 Referred: <b>{refs}</b>\n"
            "📅 Joined: <b>{since}</b>"
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
