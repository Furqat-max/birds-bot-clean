import os
import random
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Render Environment Variables dan olinadi
TOKEN = os.environ.get("BOT_TOKEN", "BOT_TOKENINGIZNI_QOYING")
WEBAPP_URL = os.environ.get("WEBAPP_URL", "https://birds-bot-clean.onrender.com")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

def generate_math_captcha():
    """Tasodifiy matematik misol va to'g'ri javobni yaratish"""
    num1 = random.randint(5, 40)
    num2 = random.randint(1, 20)
    operator = random.choice(["+", "-"])

    if operator == "+":
        correct_answer = num1 + num2
    else:
        correct_answer = num1 - num2

    question = f"{num1} {operator} {num2} = ?"
    return question, correct_answer


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Foydalanuvchi /start bosganda captcha berish"""
    question, answer = generate_math_captcha()
    
    # Foydalanuvchi xotirasiga to'g'ri javobni saqlaymiz
    context.user_data["captcha_answer"] = answer
    context.user_data["is_verified"] = False

    await update.message.reply_text(
        "👋 Assalomu alaykum!\n\n"
        "Platformaga kirishdan oldin xavfsizlik tekshiruvidan (Captcha) o‘ting.\n\n"
        f"👉 Misolni yeching: <b>{question}</b>\n"
        "<i>Javobingizni raqam shaklida yuboring:</i>",
        parse_mode="HTML"
    )


async def check_captcha_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Foydalanuvchi javob yuborganida tekshirish"""
    user_text = update.message.text.strip()
    correct_answer = context.user_data.get("captcha_answer")
    is_verified = context.user_data.get("is_verified", False)

    # Agar allaqachon tasdiqlangan bo'lsa
    if is_verified:
        keyboard = [
            [InlineKeyboardButton("🦅 O‘yinga kirish", web_app=WebAppInfo(url=WEBAPP_URL))]
        ]
        await update.message.reply_text(
            "Siz allaqachon tekshiruvdan o‘tgansiz. O‘yinga kirishingiz mumkin:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # Foydalanuvchi kiritgan javobni tekshirish
    try:
        user_num = int(user_text)
    except ValueError:
        await update.message.reply_text("Iltimos, faqat raqam kiriting!")
        return

    if user_num == correct_answer:
        # To'g'ri javob: tasdiqlandi, ball berilmaydi, darhol WebApp ochiladi
        context.user_data["is_verified"] = True
        context.user_data.pop("captcha_answer", None)

        keyboard = [
            [InlineKeyboardButton("🦅 O‘yinga kirish (WebApp)", web_app=WebAppInfo(url=WEBAPP_URL))]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "✅ <b>Xavfsizlik tekshiruvidan muvaffaqiyatli o‘tdingiz!</b>\n\n"
            "Quyidagi tugma orqali asosiy platformaga kiring:",
            reply_markup=reply_markup,
            parse_mode="HTML"
        )
    else:
        # Noto'g'ri javob: yangi misol beriladi
        new_question, new_answer = generate_math_captcha()
        context.user_data["captcha_answer"] = new_answer

        await update.message.reply_text(
            "❌ <b>Noto‘g‘ri javob!</b>\n\n"
            f"Qaytadan urinib ko‘ring: <b>{new_question}</b>",
            parse_mode="HTML"
        )


if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_captcha_reply))

    print("Telegram bot Python orqali ishga tushdi...")
    app.run_polling()

