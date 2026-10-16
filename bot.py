import os
import logging
import html
import asyncio
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    WebAppInfo,
    MenuButtonWebApp,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

# Konfiguratsiyalar va muhit o'zgaruvchilari
TOKEN = os.environ.get("BOT_TOKEN", "").strip()
raw_url = os.environ.get("WEBAPP_URL", "https://birds-bot-clean.onrender.com").strip()
WEBAPP_URL = raw_url.rstrip("/")

# Loglarni sozlash
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user

    # Foydalanuvchi ma'lumotlarini xavfsiz shakllantirish
    user_name = html.escape(user.first_name) if user and user.first_name else "Investor"
    user_id = user.id if user else "Noma'lum"

    # 1. Pastki asosiy chat menyusiga doimiy WebApp tugmasini o'rnatish
    try:
        await context.bot.set_chat_menu_button(
            chat_id=chat_id,
            menu_button=MenuButtonWebApp(
                text="🦅 Birds Invest",
                web_app=WebAppInfo(url=WEBAPP_URL)
            )
        )
    except Exception as e:
        logging.warning(f"Menyu tugmasini faollashtirishda ogohlantirish: {e}")

    # 2. Referal va ulashish havolasini tayyorlash
    bot_info = await context.bot.get_me()
    referral_link = f"https://t.me/{bot_info.username}?start=ref_{user_id}"
    share_link = f"https://t.me/share/url?url={referral_link}&text=🦅+Birds+Invest+-+Qushlar+bilan+virtual+daromad+olishni+boshlang!"

    # 3. Keng qamrovli interaktiv tugmalar paneli
    keyboard = [
        # Asosiy kirish tugmasi
        [
            InlineKeyboardButton(
                text="🚀 O‘YINNI BOSHLASH (WEBAPP)",
                web_app=WebAppInfo(url=WEBAPP_URL)
            )
        ],
        # Balans va reyting
        [
            InlineKeyboardButton(
                text="💼 Hamyon",
                web_app=WebAppInfo(url=f"{WEBAPP_URL}#wallet")
            ),
            InlineKeyboardButton(
                text="🏆 Top Reyting",
                web_app=WebAppInfo(url=f"{WEBAPP_URL}#leaders")
            ),
        ],
        # Do'stlarni taklif qilish va Jamiyat
        [
            InlineKeyboardButton(
                text="👥 Do‘stlarni taklif qilish",
                url=share_link
            ),
            InlineKeyboardButton(
                text="📢 Rasmiy Kanal",
                url="https://t.me/telegram"
            ),
        ]
    ]

    # Qalin shriflar (bold) va emojilar bilan bezatilgan chiroyli xabar
    welcome_message = (
        f"🦅 <b>BIRDS INVEST EKOTIZIMIGA XUSH KELIBSIZ!</b>\n\n"
        f"👤 <b>Investor:</b> <b>{user_name}</b>\n"
        f"🆔 <b>Hisob raqami:</b> <code>{user_id}</code>\n"
        f"📊 <b>Hisob holati:</b> 🟢 <b>Faol</b>\n"
        f"🌐 <b>Platforma versiyasi:</b> <b>v2.0 (Tezkor)</b>\n\n"
        f"━━━━━━━━━━━━━━━━━━━\n\n"
        f"🎮 <b>O‘yin imkoniyatlari:</b>\n"
        f"• <b>Qushlar sotib oling va daromadni ko‘paytiring</b>\n"
        f"• <b>Tuxumlarni yig‘ib, virtual tangalarga almashtiring</b>\n"
        f"• <b>Do‘stlaringizni taklif qilib, qo‘shimcha bonuslarga ega bo‘ling</b>\n\n"
        f"👇 <b>Darhol platformaga kirish uchun pastdagi tugmani bosing:</b>"
    )

    await update.message.reply_text(
        text=welcome_message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )


async def setup_bot():
    app = ApplicationBuilder().token(TOKEN).build()

    # Webhook va eski so'rovlarni tozalab, sof polling rejimini yoqish
    try:
        await app.bot.delete_webhook(drop_pending_updates=True)
    except Exception as e:
        logging.warning(f"Webhook reset: {e}")

    app.add_handler(CommandHandler("start", start_command))
    return app


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    app = loop.run_until_complete(setup_bot())

    print("--> Birds Invest professional boti muvaffaqiyatli ishga tushdi...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)
