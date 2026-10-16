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

# Konfiguratsiya
TOKEN = os.environ.get("BOT_TOKEN", "")
WEBAPP_URL = os.environ.get("WEBAPP_URL", "https://birds-bot-clean.onrender.com")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Kengaytirilgan va zamonaviy emoji to'plami
EMOJI_COLLECTION = [
    "🦅", "🦉", "🦆", "🦜", "🦚", "🦢", "🦁", "🐯", "🐼", "🐨",
    "🦊", "🐰", "🐺", "🦄", "🐲", "💎", "🪙", "🔥", "⚡", "🚀",
    "🪐", "🎮", "🕹️", "🎯", "🏆", "👑", "🔮", "🍕", "🍔", "🍓"
]

# Sessiyalarni xavfsiz boshqarish (In-Memory State Manager)
USER_SESSIONS = {}


def build_captcha_session(user_id: int):
    """Foydalanuvchi uchun zamonaviy 2x2 shakldagi emoji captchani generatsiya qilish"""
    # 4 ta takrorlanmas emoji tanlash
    selected_emojis = random.sample(EMOJI_COLLECTION, 4)
    target_emoji = random.choice(selected_emojis)

    # 2x2 panjara (grid) ko'rinishidagi zamonaviy tugmalar
    keyboard_grid = [
        [
            InlineKeyboardButton(
                text=selected_emojis[0],
                callback_data=f"cap:ok:{user_id}" if selected_emojis[0] == target_emoji else f"cap:no:{user_id}"
            ),
            InlineKeyboardButton(
                text=selected_emojis[1],
                callback_data=f"cap:ok:{user_id}" if selected_emojis[1] == target_emoji else f"cap:no:{user_id}"
            ),
        ],
        [
            InlineKeyboardButton(
                text=selected_emojis[2],
                callback_data=f"cap:ok:{user_id}" if selected_emojis[2] == target_emoji else f"cap:no:{user_id}"
            ),
            InlineKeyboardButton(
                text=selected_emojis[3],
                callback_data=f"cap:ok:{user_id}" if selected_emojis[3] == target_emoji else f"cap:no:{user_id}"
            ),
        ]
    ]

    USER_SESSIONS[user_id] = {
        "target": target_emoji,
        "attempts": USER_SESSIONS.get(user_id, {}).get("attempts", 0) + 1,
        "verified": False,
    }

    return target_emoji, InlineKeyboardMarkup(keyboard_grid)


def build_verified_dashboard_keyboard(bot_username: str, user_id: int):
    """Zamonaviy va murakkab WebApp boshqaruv paneli tugmalari"""
    referral_link = f"https://t.me/{bot_username}?start=ref_{user_id}"
    share_url = f"https://t.me/share/url?url={referral_link}&text=🦅+Birds+Invest+-+qushlar+bilan+sarmoyasiz+daromad+olishni+boshlang!"

    keyboard = [
        # Asosiy katta WebApp tugmasi
        [
            InlineKeyboardButton("🚀 O‘YINNI BOSHLASH (WEBAPP)", web_app=WebAppInfo(url=WEBAPP_URL))
        ],
        # Ikkinchi qator: Hamyon va Reyting
        [
            InlineKeyboardButton("💼 Hamyon & Statistika", web_app=WebAppInfo(url=f"{WEBAPP_URL}#profile")),
            InlineKeyboardButton("🏆 Top Sarmoyadorlar", web_app=WebAppInfo(url=f"{WEBAPP_URL}#leaderboard"))
        ],
        # Uchinchi qator: Do'stlarni chaqirish va Yangiliklar
        [
            InlineKeyboardButton("👥 Do‘stlarni taklif qilish", url=share_url),
            InlineKeyboardButton("📢 Rasmiy Kanal", url="https://t.me/telegram")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id
    user_id = user.id
    user_name = html.escape(user.first_name) if user and user.first_name else "Foydalanuvchi"

    # Xavfsizlik: Kirishdan oldin pastdagi WebApp tugmasini o'chirib qo'yamiz
    try:
        await context.bot.set_chat_menu_button(
            chat_id=chat_id,
            menu_button=MenuButtonDefault()
        )
    except Exception as e:
        logging.warning(f"MenuButton reset warning: {e}")

    # Agar allaqachon tasdiqlangan bo'lsa, to'g'ridan-to'g'ri o'yin panelini ochamiz
    session = USER_SESSIONS.get(user_id, {})
    if session.get("verified"):
        bot_info = await context.bot.get_me()
        await update.message.reply_text(
            f"👑 <b>Xush kelibsiz, {user_name}!</b>\n\n"
            f"🆔 <b>Sizning hisobingiz faol va xavfsiz.</b>\n"
            f"Quyidagi boshqaruv paneli orqali platformaga kiring:",
            reply_markup=build_verified_dashboard_keyboard(bot_info.username, user_id),
            parse_mode="HTML"
        )
        return

    # Yangi Captcha generatsiya qilish
    target, keyboard = build_captcha_session(user_id)

    welcome_text = (
        f"👋 <b>Assalomu alaykum, {user_name}!</b>\n\n"
        f"🛡️ <b>Birds Invest Xavfsizlik Tizimi:</b>\n"
        f"Platformaga kirish uchun bot emasligingizni tasdiqlang.\n\n"
        f"🎯 <b>Vazifa:</b> Quyidagi 2x2 panjaradan aynan <b>[ {target} ]</b> belgisini topib bosing:"
    )

    await update.message.reply_text(
        text=welcome_text,
        reply_markup=keyboard,
        parse_mode="HTML"
    )


async def handle_captcha_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    user = update.effective_user
    chat_id = update.effective_chat.id
    user_id = user.id
    user_name = html.escape(user.first_name) if user and user.first_name else "Foydalanuvchi"

    if not data or not data.startswith("cap:"):
        return

    _, status, target_uid = data.split(":")

    # Boshqa odam tugmani bosishining oldini olish
    if int(target_uid) != user_id:
        await query.answer("⚠️ Bu tekshiruv boshqa foydalanuvchiga tegishli!", show_alert=True)
        return

    if status == "ok":
        # 1. Sessiyada tasdiqlash
        USER_SESSIONS[user_id] = {"verified": True, "attempts": 0}

        # 2. Pastki doimiy WebApp Menyu tugmasini yoqish
        try:
            await context.bot.set_chat_menu_button(
                chat_id=chat_id,
                menu_button=MenuButtonWebApp(
                    text="🦅 Birds Invest",
                    web_app=WebAppInfo(url=WEBAPP_URL)
                )
            )
        except Exception as e:
            logging.warning(f"MenuButton enable warning: {e}")

        bot_info = await context.bot.get_me()

        success_text = (
            f"✅ <b>Xavfsizlik tekshiruvi muvaffaqiyatli yakunlandi!</b>\n\n"
            f"👤 <b>Foydalanuvchi:</b> {user_name}\n"
            f"💎 <b>Status:</b> Tasdiqlangan Investor\n"
            f"🌐 <b>Platforma:</b> Tayyor\n\n"
            f"<i>Pastdagi tugmalar yoki menyu orqali darhol WebApp platformasiga o‘tishingiz mumkin:</i>"
        )

        await query.edit_message_text(
            text=success_text,
            reply_markup=build_verified_dashboard_keyboard(bot_info.username, user_id),
            parse_mode="HTML"
        )
    else:
        # Noto'g'ri emoji bosilganda
        target, new_keyboard = build_captcha_session(user_id)
        attempts = USER_SESSIONS[user_id]["attempts"]

        fail_text = (
            f"❌ <b>Noto‘g‘ri belgi tanlandi!</b>\n\n"
            f"Iltimos, diqqat bilan qarang va quyidagi 2x2 panjaradan aynan <b>[ {target} ]</b> belgisini bosing:\n"
            f"<i>(Urinish: #{attempts})</i>"
        )

        await query.edit_message_text(
            text=fail_text,
            reply_markup=new_keyboard,
            parse_mode="HTML"
        )


if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CallbackQueryHandler(handle_captcha_callback))

    print("🦅 Birds Invest Murakkab Bot Polling Tizimi Ishga Tushdi...")
    app.run_polling(drop_pending_updates=True)
