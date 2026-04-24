import sys
import os
import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from telegram.error import TelegramError

# Добавляем parent directory в path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import telegram_token
from db.functions import init_db, save_user, get_user
from utils import retry

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

TOKEN = telegram_token


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.effective_user
        logger.info(f"Пользователь {user.id} ({user.first_name}) запустил бота")

        button = KeyboardButton("Accept to Human", request_contact=True)
        keyboard = ReplyKeyboardMarkup([[button]], resize_keyboard=True)

        await update.message.reply_text(
            f"Привет, {user.first_name}!\n\n"
            "For continue press 👇",
            reply_markup=keyboard
        )
    except TelegramError as e:
        logger.error(f"Telegram ошибка в /start: {e}")
        try:
            await update.message.reply_text("❌ Произошла ошибка. Попробуйте позже.")
        except:
            pass
    except Exception as e:
        logger.error(f"Критическая ошибка в /start: {e}", exc_info=True)


async def contact_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        contact = update.message.contact
        user_id = update.effective_user.id

        if contact.user_id != user_id:
            logger.warning(f"Пользователь {user_id} попытался отправить контакт другого юзера")
            await update.message.reply_text("❌ Отправьте ВАШ контакт")
            return

        phone = contact.phone_number
        name = update.effective_user.first_name

        # Валидация номера
        if not phone or len(phone) < 7:
            logger.warning(f"Некорректный номер: {phone}")
            await update.message.reply_text("❌ Некорректный номер телефона")
            return

        # Сохраняем в базу
        save_user(user_id, name, phone)
        logger.info(f"✅ Сохранён пользователь: {name} ({user_id}) — {phone}")

        # Удаляем сообщение с номером безопасно
        try:
            await update.message.delete()
        except TelegramError as e:
            logger.warning(f"Не удалось удалить сообщение контакта: {e}")

        await update.message.reply_text(
            "You are Human ✅",
            reply_markup=ReplyKeyboardRemove()
        )
    except TelegramError as e:
        logger.error(f"Telegram ошибка в contact_handler: {e}")
        try:
            await update.message.reply_text("❌ Ошибка сохранения. Попробуйте ещё раз.")
        except:
            pass
    except Exception as e:
        logger.error(f"Критическая ошибка в contact_handler: {e}", exc_info=True)


async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        user = get_user(user_id)

        if user is None:
            logger.info(f"Неавторизованный пользователь {user_id} отправил сообщение")
            await update.message.reply_text(
                "❗❗❗ Accept your Humanity at first ❗❗❗"
            )
        else:
            logger.info(f"Пользователь {user_id} отправил текстовое сообщение")
            await update.message.reply_text("Ты уже авторизован 👍")
    except TelegramError as e:
        logger.error(f"Telegram ошибка в text_handler: {e}")
    except Exception as e:
        logger.error(f"Критическая ошибка в text_handler: {e}", exc_info=True)


def start_bot():
    """Запускает телеграм-бота с обработкой ошибок"""
    try:
        init_db()  # Создаём таблицу при запуске
        logger.info("🤖 Инициализация телеграм-бота...")
        
        @retry(max_attempts=3, delay=2.0)
        def _build_app():
            """Создание приложения с автоматическими повторами"""
            app = ApplicationBuilder().token(TOKEN).build()
            return app
        
        app = _build_app()
        
        # Добавляем обработчики
        app.add_handler(CommandHandler("start", start))
        app.add_handler(MessageHandler(filters.CONTACT, contact_handler))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
        
        logger.info("✅ Бот готов к работе")
        
        # Запуск polling без retry - встроенный механизм переподключения уже есть
        app.run_polling(allowed_updates=None)
    
    except ValueError as e:
        logger.error(f"❌ Ошибка конфигурации: {e}")
        sys.exit(1)
    except TelegramError as e:
        logger.error(f"❌ Telegram ошибка: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    start_bot()
