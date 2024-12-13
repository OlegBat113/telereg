# Сначала импортируем настройки Django
import django_setup

# Затем все остальные импорты
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler
from django.conf import settings
from django.contrib.auth.models import User
from teleregapp.models import TelegramUser
import asyncio
import platform
import signal
import sys
from asgiref.sync import sync_to_async

logger = logging.getLogger('bot')

# Создаем асинхронные версии операций с базой данных
get_telegram_user = sync_to_async(TelegramUser.objects.filter)
create_user = sync_to_async(User.objects.create_user)
create_telegram_user = sync_to_async(TelegramUser.objects.create)
check_token_exists = sync_to_async(TelegramUser.objects.filter)

async def start(update, context):
    token = context.args[0] if context.args else None
    telegram_id = update.effective_user.id
    username = update.effective_user.username
    
    logger.info(f"Получена команда start от пользователя {username} (ID: {telegram_id})")
    logger.info(f"Аргументы команды: {context.args}")
    
    if not token:
        logger.warning(f"Попытка авторизации без токена от пользователя {telegram_id}")
        await update.message.reply_text(
            "Ошибка авторизации: отсутствует токен.\n"
            "Пожалуйста, перейдите по ссылке из веб-приложения."
        )
        return

    logger.info(f"Начало авторизации пользователя {username} (ID: {telegram_id}) с токеном {token}")

    try:
        # Проверяем, существует ли пользователь с таким telegram_id
        existing_user = await get_telegram_user(telegram_id=telegram_id)
        existing_user = await sync_to_async(lambda: existing_user.first())()
        
        if existing_user:
            # Обновляем токен существующего пользователя
            existing_user.auth_token = token
            await sync_to_async(existing_user.save)()
            logger.info(f"Обновлен токен для существующего пользователя {username}")
            await update.message.reply_text(
                "Авторизация успешна!\n"
                "Теперь вы можете вернуться в браузер."
            )
            return

        # Проверяем, не используется ли уже этот токен
        token_exists = await check_token_exists(auth_token=token)
        if await sync_to_async(lambda: token_exists.exists())():
            logger.warning(f"Попытка использовать уже существующий токен: {token}")
            await update.message.reply_text(
                "Ошибка: токен уже использован.\n"
                "Пожалуйста, вернитесь в браузер и попробуйте еще раз."
            )
            return

        # Создаем нового пользователя
        user = await create_user(
            username=f"tg_{telegram_id}",
            password=None
        )
        
        telegram_user = await create_telegram_user(
            user=user,
            telegram_id=telegram_id,
            username=username,
            auth_token=token
        )
        
        logger.info(f"Создан новый пользователь {username}")
        await update.message.reply_text(
            "Авторизация успешна!\n"
            "Теперь вы можете вернуться в браузер."
        )
        
    except Exception as e:
        logger.error(f"Ошибка при авторизации пользователя {username}: {str(e)}", exc_info=True)
        await update.message.reply_text(
            "Произошла ошибка при авторизации.\n"
            "Пожалуйста, вернитесь в браузер и попробуйте еще раз."
        )

async def run_bot():
    logger.info("Запуск бота")
    application = None
    try:
        application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
        application.add_handler(CommandHandler("start", start))
        logger.info("Бот успешно запущен")
        await application.initialize()
        await application.start()
        await application.updater.start_polling()
        
        while True:
            await asyncio.sleep(1)
            
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {str(e)}", exc_info=True)
    finally:
        if application:
            if application.updater:
                await application.updater.stop()
            await application.stop()
            await application.shutdown()

def signal_handler(signum, frame):
    logger.info(f"Получен сигнал {signum}")
    sys.exit(0)

def setup_signals():
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

if __name__ == '__main__':
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    setup_signals()
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(run_bot())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Критическая ошибка: {str(e)}", exc_info=True)
    finally:
        try:
            pending = asyncio.all_tasks(loop)
            for task in pending:
                task.cancel()
            
            if pending:
                loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
            
            loop.close()
        except Exception as e:
            logger.error(f"Ошибка при закрытии цикла событий: {str(e)}", exc_info=True) 