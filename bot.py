import os
import logging
import html
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    WebAppInfo,
    MenuButtonWebApp,
    BotCommand,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

# Muhit o'zgaruvchilari
TOKEN = os.environ.get("BOT_TOKEN", "").strip()
raw_url = os.environ.get("WEBAPP_URL", "https://birds-bot-clean.onrender.com").strip()
WEBAPP_URL = raw_url.rstrip("/")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)


async def post_init(application):
    """Bot ishga tushishi bilan menyu buyruqlarini avtomatik sozlaydi"""
    commands = [
        BotCommand("start", "Boshqaruv paneli"),
        BotCommand("help", "Yordam markazi")
    ]
    await application.bot.set_my_commands(commands)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user

    user_name = html.escape(user.first_name) if user and user.first_name else "Investor"
    user_id = user.id if user else "Noma'lum"

    # Pastki doimiy menyu tugmasini ulash
    try:
        await context.bot.set_chat_menu_button(
            chat_id=chat_id,
            menu_button=MenuButtonWebApp(
                text="🦅 Birds Invest",
                web_app=WebAppInfo(url=WEBAPP_URL)
            )
        )
    except Exception as e:
        logging.warning(f"MenuButton sozlashda ogohlantirish: {e}")

    bot_info = await context.bot.get_me()
    referral_link = f"https://t.me/{bot_info.username}?start=ref_{user_id}"
    share_link = f"https://t.me/share/url?url={referral_link}&text=🦅+Birds+Invest+-+Qushlar+bilan+virtual+daromad+olishni+boshlang!"

    keyboard = [
        [
            InlineKeyboardButton(
                text="🚀 O‘YINNI BOSHLASH (WEBAPP)",
                web_app=WebAppInfo(url=WEBAPP_URL)
            )
        ],
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

    welcome_message = (
        f"🦅 <b>BIRDS INVEST EKOTIZIMIGA XUSH KELIBSIZ!</b>\n\n"
        f"👤 <b>Investor:</b> <b>{user_name}</b>\n"
        f"🆔 <b>Hisob raqami:</b> <code>{user_id}</code>\n"
        f"📊 <b>Hisob holati:</b> 🟢 <b>Faol</b>\n"
        f"🌐 <b>Platforma:</b> <b>v2.0 (Tezkor)</b>\n\n"
        f"━━━━━━━━━━━━━━━━━━━\n\n"
        f"🎮 <b>O‘yin imkoniyatlari:</b>\n"
        f"• <b>Qushlar sotib oling va ko‘proq tuxum yig‘ing</b>\n"
        f"• <b>Tuxumlarni soting va virtual tangalarni jamg‘aring</b>\n"
        f"• <b>Do‘stlaringizni taklif qilib, qo‘shimcha daromad oling</b>\n\n"
        f"👇 <b>Platformaga kirish uchun pastdagi tugmani bosing:</b>"
    )

    await update.message.reply_text(
        text=welcome_message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_name = html.escape(user.first_name) if user and user.first_name else "Foydalanuvchi"

    help_keyboard = [
        [
            InlineKeyboardButton(
                text="🚀 O‘yinni ochish",
                web_app=WebAppInfo(url=WEBAPP_URL)
            )
        ],
        [
            InlineKeyboardButton(
                text="👨‍💻 Qo‘llab-quvvatlash xizmati",
                url="https://t.me/telegram"
            ),
            InlineKeyboardButton(
                text="📢 Yangiliklar kanali",
                url="https://t.me/telegram"
            )
        ]
    ]

    help_message = (
        f"📖 <b>BIRDS INVEST — YORDAM VA QO‘LLANMA MARKAZI</b>\n\n"
        f"Hurmatli <b>{user_name}</b>, platformadan unumli foydalanish bo‘yicha qo‘llanma:\n\n"
        f"━━━━━━━━━━━━━━━━━━━\n\n"
        f"❓ <b>QANDAY O‘YNASH KERAK?</b>\n"
        f"1️⃣ <b>Qushlar bo‘limi:</b> Har xil turdagi qushlarni xarid qiling.\n"
        f"2️⃣ <b>Omborxona (Tuxumlar):</b> Qushlar to‘plagan mahsulotlarni omborga yig‘ib boring.\n"
        f"3️⃣ <b>Bozor:</b> Tuxumlarni soting va tangalarga almashtiring.\n"
        f"4️⃣ <b>Yechib olish:</b> Yig‘ilgan mablag‘larni qulay usulda yechib oling.\n\n"
        f"━━━━━━━━━━━━━━━━━━━\n\n"
        f"👥 <b>REFERAL DASTURI:</b>\n"
        f"• O‘z havolangiz orqali do‘stlaringizni taklif qiling va doimiy bonuslarga ega bo‘ling.\n\n"
        f"💬 <b>Savollaringiz bormi?</b>\n"
        f"Qo‘shimcha savollar bo‘lsa, quyidagi yordam tugmasi orqali admin bilan bog‘laning:"
    )

    await update.message.reply_text(
        text=help_message,
        reply_markup=InlineKeyboardMarkup(help_keyboard),
        parse_mode="HTML"
    )


def main():
    if not TOKEN:
        print("XATOLIK: BOT_TOKEN topilmadi!")
        return

    # Asosiy bot ilovasini yaratish
    app = ApplicationBuilder().token(TOKEN).post_init(post_init).build()

    # Buyruqlarni qo'shish
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))

    print("🦅 Birds Invest Bot muvaffaqiyatli ishga tushdi va ulandi...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
