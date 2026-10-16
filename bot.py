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
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = os.environ.get("BOT_TOKEN", "")
WEBAPP_URL = os.environ.get("WEBAPP_URL", "https://birds-bot-clean.onrender.com")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Xotirada vaqtincha captcha natijalarini saqlash
CAPTCHA_STORAGE = {}

def generate_math_captcha():
    num1 = random.randint(10, 30)
    num2 = random.randint(1, 15)
    operator = random.choice(["+", "-"])

    if operator == "+":
        ans = num1 + num2
    else:
        ans = num1 - num2

    text = f"{num1} {operator} {num2} = ?"
    return text, ans


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id
    user_name = html.escape(user.first_name) if user and user.first_name else "Foydalanuvchi"

    # 1. Pastdagi menyu tugmasini darhol o'chirib, oddiy holatga qaytarish
    try:
        await context.bot.set_chat_menu_button(
            chat_id=chat_id,
            menu_button=MenuButtonDefault()
        )
    except Exception as e:
        logging.warning(f"MenuButton reset error: {e}")

    # 2. Yangi misol yaratish va saqlash
    question, ans = generate_math_captcha()
    CAPTCHA_STORAGE[chat_id] = {
        "answer": ans,
        "verified": False
    }

    await update.message.reply_text(
        f"👋 <b>Assalomu alaykum, {user_name}!</b>\n\n"
        "Platformaga kirishdan oldin xavfsizlik tekshiruvidan (Captcha) o‘ting.\n\n"
        f"👉 Misolni yeching: <b>{question}</b>\n"
        "<i>Javobingizni raqam shaklida yuboring:</i>",
        parse_mode="HTML"
    )


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    text = update.message.text.strip()
    if text.startswith("/"):
        return  # buyruqlarni o'tkazib yuboramiz

    chat_id = update.effective_chat.id
    user = update.effective_user
    user_name = html.escape(user.first_name) if user and user.first_name else "Foydalanuvchi"

    data = CAPTCHA_STORAGE.get(chat_id)

    # Agar foydalanuvchi /start bosmagan bo'lsa
    if not data:
        await start_command(update, context)
        return

    # Agar allaqachon tasdiqlangan bo'lsa
    if data.get("verified"):
        keyboard = [
            [InlineKeyboardButton("🦅 O‘yinga kirish", web_app=WebAppInfo(url=WEBAPP_URL))]
        ]
        await update.message.reply_text(
            f"Hurmatli <b>{user_name}</b>, siz tekshiruvdan o‘tgansiz:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML"
        )
        return

    # Javobni solishtiramiz
    correct = data.get("answer")
    try:
        user_val = int(text)
    except ValueError:
        await update.message.reply_text("Iltimos, faqat son kiriting!")
        return

    if user_val == correct:
        data["verified"] = True

        # ENDI PASTDAGI MENYU TUGMASINI YOQAMIZ
        try:
            await context.bot.set_chat_menu_button(
                chat_id=chat_id,
                menu_button=MenuButtonWebApp(
                    text="🦅 Birds Invest",
                    web_app=WebAppInfo(url=WEBAPP_URL)
                )
            )
        except Exception as e:
            logging.warning(f"MenuButton set error: {e}")

        # Xabar ostidagi WebApp tugmasi
        keyboard = [
            [InlineKeyboardButton("🦅 O‘yinga kirish (WebApp)", web_app=WebAppInfo(url=WEBAPP_URL))]
        ]
        await update.message.reply_text(
            f"✅ <b>Tabriklaymiz, {user_name}!</b>\n\n"
            "Xavfsizlik tekshiruvidan muvaffaqiyatli o‘tdingiz.\n"
            "Quyidagi tugma orqali platformaga kiring:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML"
        )
    else:
        new_q, new_ans = generate_math_captcha()
        data["answer"] = new_ans

        await update.message.reply_text(
            f"❌ <b>Noto‘g‘ri javob, {user_name}!</b>\n\n"
            f"Qayta urinib ko‘ring: <b>{new_q}</b>",
            parse_mode="HTML"
        )


if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.ALL, message_handler))

    app.run_polling()
