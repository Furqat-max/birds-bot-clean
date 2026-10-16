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

def generate_math_captcha():
    num1 = random.randint(10, 40)
    num2 = random.randint(1, 20)
    operator = random.choice(["+", "-"])

    if operator == "+":
        correct_answer = num1 + num2
    else:
        correct_answer = num1 - num2

    question = f"{num1} {operator} {num2} = ?"
    return question, correct_answer


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user
    user_name = html.escape(user.first_name) if user and user.first_name else "Foydalanuvchi"

    # 1. Pastdagi WebApp Menyu tugmasini darhol yashiramiz (standart holatga qaytaramiz)
    try:
        await context.bot.set_chat_menu_button(
            chat_id=chat_id,
            menu_button=MenuButtonDefault()
        )
    except Exception as e:
        logging.error(f"Menu buttonni yashirishda xatolik: {e}")

    question, answer = generate_math_captcha()
    
    context.user_data["captcha_answer"] = answer
    context.user_data["is_verified"] = False

    await update.message.reply_text(
        f"👋 <b>Assalomu alaykum, {user_name}!</b>\n\n"
        "Platformaga kirishdan oldin xavfsizlik tekshiruvidan (Captcha) o‘ting.\n\n"
        f"👉 Misolni yeching: <b>{question}</b>\n"
        "<i>Javobingizni raqam shaklida yuboring:</i>",
        parse_mode="HTML"
    )


async def check_captcha_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    chat_id = update.effective_chat.id
    user = update.effective_user
    user_name = html.escape(user.first_name) if user and user.first_name else "Foydalanuvchi"

    user_text = update.message.text.strip()
    correct_answer = context.user_data.get("captcha_answer")
    is_verified = context.user_data.get("is_verified", False)

    # Agar foydalanuvchi allaqachon tekshiruvdan o'tgan bo'lsa
    if is_verified:
        keyboard = [
            [InlineKeyboardButton("🦅 O‘yinga kirish", web_app=WebAppInfo(url=WEBAPP_URL))]
        ]
        await update.message.reply_text(
            f"Hurmatli <b>{user_name}</b>, siz allaqachon tekshiruvdan o‘tgansiz. O‘yinga kirishingiz mumkin:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML"
        )
        return

    # Kiritilgan javobni tekshirish
    try:
        user_num = int(user_text)
    except ValueError:
        await update.message.reply_text("Iltimos, faqat raqam shaklida javob bering!")
        return

    if correct_answer is not None and user_num == int(correct_answer):
        # 1. Holatni tasdiqlaymiz
        context.user_data["is_verified"] = True
        context.user_data.pop("captcha_answer", None)

        # 2. ENDI PASTDAGI MENYU TUGMASINI YOQAMIZ (Faqat to'g'ri yechganidan keyin chiqadi)
        try:
            await context.bot.set_chat_menu_button(
                chat_id=chat_id,
                menu_button=MenuButtonWebApp(
                    text="🦅 Birds Invest",
                    web_app=WebAppInfo(url=WEBAPP_URL)
                )
            )
        except Exception as e:
            logging.error(f"Menu buttonni yoqishda xatolik: {e}")

        # Xabar ostidagi tugma
        keyboard = [
            [InlineKeyboardButton("🦅 O‘yinga kirish (WebApp)", web_app=WebAppInfo(url=WEBAPP_URL))]
        ]
        await update.message.reply_text(
            f"✅ <b>Tabriklaymiz, {user_name}!</b>\n\n"
            "Xavfsizlik tekshiruvidan muvaffaqiyatli o‘tdingiz.\n"
            "Pastdagi menyu tugmasi va quyidagi havola orqali platformaga kiring:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML"
        )
    else:
        # Noto'g'ri javob kiritilsa, yangi misol beriladi
        new_question, new_answer = generate_math_captcha()
        context.user_data["captcha_answer"] = new_answer

        await update.message.reply_text(
            f"❌ <b>Noto‘g‘ri javob, {user_name}!</b>\n\n"
            f"Qaytadan urinib ko‘ring: <b>{new_question}</b>",
            parse_mode="HTML"
        )


if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), check_captcha_reply))

    app.run_polling()
