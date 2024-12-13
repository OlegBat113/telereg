from telegram.ext import Updater, CommandHandler
from django.conf import settings
from teleregapp.models import TelegramUser
from django.contrib.auth.models import User
import logging

logger = logging.getLogger('bot')

def start(update, context):
    token = context.args[0] if context.args else None
    telegram_id = update.effective_user.id
    username = update.effective_user.username
    
    if not token:
        logger.warning(f"Попытка авторизации без токена от пользователя {telegram_id}")
        update.message.reply_text("Ошибка авторизации")
        return

    logger.info(f"Начало авторизации пользователя {username} (ID: {telegram_id}) с токеном {token}")

    try:
        user = User.objects.create_user(username=f"tg_{telegram_id}")
        telegram_user = TelegramUser.objects.create(
            user=user,
            telegram_id=telegram_id,
            username=username,
            auth_token=token
        )
        logger.info(f"Успешная авторизация пользователя {username}")
        update.message.reply_text("Авторизация успешна!")
    except Exception as e:
        logger.error(f"Ошибка при авторизации пользователя {username}: {str(e)}", exc_info=True)
        update.message.reply_text("Произошла ошибка при авторизации")

def main():
    logger.info("Запуск бота")
    try:
        updater = Updater(settings.TELEGRAM_BOT_TOKEN)
        dp = updater.dispatcher
        dp.add_handler(CommandHandler("start", start))
        updater.start_polling()
        logger.info("Бот успешно запущен")
        updater.idle()
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {str(e)}", exc_info=True)

if __name__ == '__main__':
    main() 