import os
import random
import logging
import html
import asyncio
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

TOKEN = os.environ.get("BOT_TOKEN", "").strip()
raw_url = os.environ.get("WEBAPP_URL", "https://birds-bot-clean.onrender.com").strip()
# URL oxiridagi / belgilarni va ortiqcha bo'shliqlarni olib tashlaymiz
WEBAPP_URL = raw_url.rstrip("/")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

EMOJI_COLLECTION = [
    "🦅", "🦉", "🦁", "🐯", "🐼", "🦊", "🐰", "🐺",
    "💎", "🪙", "🔥", "⚡", "🚀", "🎮", "🎯", "🏆"
]

USER_TARGETS = {}

def generate_matrix_captcha(user_id: int):
    selected = random.sample(EMOJI_COLLECTION, 4)
    target = random.choice(selected)
    USER_TARGETS[user_id] = target

    buttons = [
        [
            InlineKeyboardButton(text=selected[0], callback_data=f"click_{selected[0]}"),
            InlineKeyboardButton(text=selected[1], callback_data=f"click_{selected[1]}")
        ],
        [
            InlineKeyboardButton(text=selected[2], callback_data=f"click_{selected[2]}"),
            InlineKeyboardButton(text=selected[3], callback_data=f"click_{selected[3]}")
        ]
    ]
    return target, InlineKeyboardMarkup(buttons)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user
    user_name = html.escape(user.first_name) if user and user.first_name else "Foydalanuvchi"

    # Pastdagi tugmani boshlang'ich oddiy holatga qaytaramiz
    try:
        await context.bot.set_chat_menu_button(
            chat_id=chat_id,
            menu_button=MenuButtonDefault()
        )
    except Exception as e:
        logging.warning(f"MenuDefault xatosi: {e}")

    target, keyboard = generate_matrix_captcha(user.id)

    await update.message.reply_text(
        f"👋 <b>Assalomu alaykum, {user_name}!</b>\n\n"
        f"🛡️ <b>Birds Invest Xavfsizlik Tekshiruvi</b>\n"
        f"Iltimos, bot emasligingizni tasdiqlang.\n\n"
        f"👉 <b>Quyidagi 4 ta belgidan aynan [ {target} ] belgisini bosing:</b>",
        reply_markup=keyboard,
        parse_mode="HTML"
    )


async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    
    # Tugma bosilgandagi Telegram animatsiyasini darhol to'xtatish
    try:
        await query.answer()
    except Exception:
        pass

    user = update.effective_user
    chat_id = update.effective_chat.id
    user_name = html.escape(user.first_name) if user and user.first_name else "Foydalanuvchi"

    clicked_emoji = query.data.replace("click_", "")
    target_emoji = USER_TARGETS.get(user.id)

    if clicked_emoji == target_emoji:
        # 1. Pastdagi WebApp Menyu tugmasini yoqishga urinamiz
        try:
            await context.bot.set_chat_menu_button(
                chat_id=chat_id,
                menu_button=MenuButtonWebApp(
                    text="🦅 Birds Invest",
                    web_app=WebAppInfo(url=WEBAPP_URL)
                )
            )
        except Exception as err:
            logging.error(f"set_chat_menu_button xatosi (URL noto'g'ri bo'lishi mumkin): {err}")

        # 2. Xabar ostidagi tugmalarni tuzamiz
        try:
            dashboard = [
                [InlineKeyboardButton("🚀 O‘YINNI BOSHLASH (WEBAPP)", web_app=WebAppInfo(url=WEBAPP_URL))],
                [
                    InlineKeyboardButton("🌐 Veb-saytga o‘tish", url=WEBAPP_URL)
                ]
            ]
            keyboard_markup = InlineKeyboardMarkup(dashboard)
        except Exception as btn_err:
            logging.error(f"Tugma yaratishda xato: {btn_err}")
            # Agar WebAppInfo xato bersa, zaxira sifatida oddiy link tugma beradi
            keyboard_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("🚀 O‘YINGA KIRISH", url=WEBAPP_URL)]
            ])

        # 3. Xabarni yangilash
        success_text = (
            f"✅ <b>Tabriklaymiz, {user_name}!</b>\n\n"
            f"Xavfsizlik tekshiruvidan muvaffaqiyatli o‘tdingiz.\n\n"
            f"Quyidagi tugma orqali platformaga kiring:"
        )

        try:
            await query.edit_message_text(
                text=success_text,
                reply_markup=keyboard_markup,
                parse_mode="HTML"
            )
        except Exception as edit_err:
            logging.error(f"edit_message_text xatosi: {edit_err}")
            # Agar tahrirlab bo'lmasa, yangi xabar qilib yuboradi
            await context.bot.send_message(
                chat_id=chat_id,
                text=success_text,
                reply_markup=keyboard_markup,
                parse_mode="HTML"
            )

    else:
        # Noto'g'ri bosilganda yangi belgi berish
        new_target, new_keyboard = generate_matrix_captcha(user.id)
        fail_text = (
            f"❌ <b>Noto‘g‘ri belgi!</b>\n\n"
            f"Qaytadan urinib ko‘ring. Endi aynan <b>[ {new_target} ]</b> belgisini bosing:"
        )
        try:
            await query.edit_message_text(
                text=fail_text,
                reply_markup=new_keyboard,
                parse_mode="HTML"
            )
        except Exception:
            pass


async def setup_bot():
    app = ApplicationBuilder().token(TOKEN).build()
    try:
        await app.bot.delete_webhook(drop_pending_updates=True)
    except Exception as e:
        logging.warning(f"Webhook o'chirishda ogohlantirish: {e}")

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CallbackQueryHandler(handle_button))
    return app


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    app = loop.run_until_complete(setup_bot())

    print("🦅 Birds Invest Bot to'liq tayyor va ishlamoqda...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)
