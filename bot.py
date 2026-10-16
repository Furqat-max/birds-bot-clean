import os
import random
import logging
import html
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    WebAppInfo,
    MenuButtonWebApp,
    MenuButtonDefault,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

TOKEN = os.environ.get("BOT_TOKEN", "")
WEBAPP_URL = os.environ.get("WEBAPP_URL", "https://birds-bot-clean.onrender.com")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Hayvonlar va qushlar ro'yxati
ANIMALS = [
    ("🦁 Sher", "wrong"),
    ("🐯 Yo‘lbars", "wrong"),
    ("🐘 Fil", "wrong"),
    ("🐺 Bo‘ri", "wrong"),
    ("🦊 Tulki", "wrong"),
    ("🐻 Ayiq", "wrong"),
]
CORRECT_BIRD = ("🦅 Qush", "correct")


def get_captcha_keyboard():
    # 3 ta boshqa hayvon va 1 ta to'g'ri qushni tanlaymiz
    options = random.sample(ANIMALS, 3) + [CORRECT_BIRD]
    random.shuffle(options)  # Joylarini aralashtiramiz

    buttons = [
        [InlineKeyboardButton(text, callback_data=data)]
        for text, data in options
    ]
    return InlineKeyboardMarkup(buttons)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user
    user_name = html.escape(user.first_name) if user and user.first_name else "Foydalanuvchi"

    # Pastdagi WebApp tugmasini yashirish (oddiy holatga qaytarish)
    try:
        await context.bot.set_chat_menu_button(
            chat_id=chat_id,
            menu_button=MenuButtonDefault()
        )
    except Exception as e:
        logging.warning(f"Menu button reset xatosi: {e}")

    await update.message.reply_text(
        f"👋 <b>Assalomu alaykum, {user_name}!</b>\n\n"
        "Platformaga kirish uchun xavfsizlik tekshiruvidan o‘ting.\n\n"
        "👉 <b>Quyidagi tugmalardan QUSH (🦅) belgisini bosing:</b>",
        reply_markup=get_captcha_keyboard(),
        parse_mode="HTML"
    )


async def captcha_button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    chat_id = update.effective_chat.id
    user = update.effective_user
    user_name = html.escape(user.first_name) if user and user.first_name else "Foydalanuvchi"

    if query.data == "correct":
        # TO'G'RI TANLANDI: Pastki menyuni yoqamiz
        try:
            await context.bot.set_chat_menu_button(
                chat_id=chat_id,
                menu_button=MenuButtonWebApp(
                    text="🦅 Birds Invest",
                    web_app=WebAppInfo(url=WEBAPP_URL)
                )
            )
        except Exception as e:
            logging.warning(f"Menu button set xatosi: {e}")

        # WebApp tugmasi bilan kutib olamiz
        keyboard = [
            [InlineKeyboardButton("🦅 O‘yinga kirish (WebApp)", web_app=WebAppInfo(url=WEBAPP_URL))]
        ]
        await query.edit_message_text(
            f"✅ <b>Tabriklaymiz, {user_name}!</b>\n\n"
            "Xavfsizlik tekshiruvidan muvaffaqiyatli o‘tdingiz.\n"
            "Pastdagi menyu yoki quyidagi tugma orqali platformaga kiring:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML"
        )
    else:
        # NOTO'G'RI TANLANDI: Yangi variantlar bilan qayta beramiz
        await query.edit_message_text(
            f"❌ <b>Noto‘g‘ri tanlov, {user_name}!</b>\n\n"
            "Iltimos, diqqat bilan <b>QUSH (🦅)</b> belgisini tanlang:",
            reply_markup=get_captcha_keyboard(),
            parse_mode="HTML"
        )


if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CallbackQueryHandler(captcha_button_click))

    print("Bot muvaffaqiyatli ishga tushdi...")
    app.run_polling()
