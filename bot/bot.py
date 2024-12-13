# Сначала импортируем настройки Django
import django_setup

# Затем все остальные импорты
import logging
# Импортируем класс Update из библиотеки telegram
from telegram import Update
# Импортируем класс Application из библиотеки telegram.ext
from telegram.ext import Application, CommandHandler
# Импортируем настройки Django
from django.conf import settings
# Импортируем класс User из библиотеки django.contrib.auth.models
from django.contrib.auth.models import User
# Импортируем класс TelegramUser из модели teleregapp.models
from teleregapp.models import TelegramUser
# Импортируем библиотеку asyncio
import asyncio
# Импортируем библиотеку platform
import platform
# Импортируем библиотеку signal
import signal
# Импортируем библиотеку sys
import sys
# Импортируем библиотеку sync_to_async из библиотеки asgiref.sync
from asgiref.sync import sync_to_async

logger = logging.getLogger('bot')

# Создаем асинхронные версии операций с базой данных
get_telegram_user = sync_to_async(TelegramUser.objects.filter)
create_user = sync_to_async(User.objects.create_user)
create_telegram_user = sync_to_async(TelegramUser.objects.create)
check_token_exists = sync_to_async(TelegramUser.objects.filter)

# Обработчик команды /start
async def start(update, context):
    token = context.args[0] if context.args else None
    telegram_id = update.effective_user.id
    username = update.effective_user.username
    
    logger.info(f"Получена команда start от пользователя {username} (ID: {telegram_id})")
    logger.info(f"Аргументы команды: {context.args}")
    
    # Проверяем, есть ли токен
    if not token:
        logger.warning(f"Попытка авторизации без токена от пользователя {telegram_id}")
        await update.message.reply_text("Ошибка авторизации: отсутствует токен.\n")
        return

    logger.info(f"Начало авторизации пользователя {username} (ID: {telegram_id}) с токеном {token}")

    try:
        # Проверяем, существует ли пользователь с таким telegram_id
        existing_user = await get_telegram_user(telegram_id=telegram_id)
        existing_user = await sync_to_async(lambda: existing_user.first())()

        # Если пользователь существует, то обновляем токен
        if existing_user:
            # Обновляем токен существующего пользователя
            existing_user.auth_token = token
            await sync_to_async(existing_user.save)()
            logger.info(f"Обновлен токен для существующего пользователя {username}")
            await update.message.reply_text(
                "Авторизация успешна!\n"
                "Закройте это окно. Вы можете вернуться на страницу авторизации."
            )
            return

        # Проверяем, не используется ли уже этот токен
        token_exists = await check_token_exists(auth_token=token)

        # Если токен уже используется, то отправляем сообщение об ошибке
        if await sync_to_async(lambda: token_exists.exists())():
            logger.warning(f"Попытка использовать уже существующий токен: {token}")
            await update.message.reply_text(
                "Ошибка: токен уже использован.\n"
                "Пожалуйста, вернитесь в окно, где проходили регистрацию."
            )
            return

        # Создаем нового пользователя
        user = await create_user(
            username=f"tg_{telegram_id}",
            password=None
        )
        
        # Создаем нового пользователя в базе данных
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
    
    # Если возникла ошибка, то отправляем сообщение об ошибке
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
        # Создаем бота
        application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
        # Добавляем обработчик команды /start
        application.add_handler(CommandHandler("start", start))
        logger.info("Бот успешно запущен")

        # Инициализируем бот
        await application.initialize()
        # Запускаем бот
        await application.start()
        # Запускаем обновление бота
        await application.updater.start_polling()
        
        while True:
            await asyncio.sleep(1)
            
    # Если возникла ошибка, то отправляем сообщение об ошибке
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {str(e)}", exc_info=True)
    finally:
        # Если бот запущен, то останавливаем его
        if application:
            if application.updater:
                await application.updater.stop()
            await application.stop()
            await application.shutdown()

# Обработчик сигналов
def signal_handler(signum, frame):
    logger.info(f"Получен сигнал {signum}")
    sys.exit(0)

# Устанавливаем обработчики сигналов
def setup_signals():
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

# Запускаем бот
if __name__ == '__main__':
    if platform.system() == 'Windows':
        # Устанавливаем политику событий для Windows
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    # Устанавливаем обработчики сигналов
    setup_signals()
    
    # Запускаем бот
    try:
        # Создаем новый цикл событий
        loop = asyncio.new_event_loop()
        # Устанавливаем цикл событий
        asyncio.set_event_loop(loop)
        # Запускаем бот
        loop.run_until_complete(run_bot())
    except KeyboardInterrupt:
        # Если пользователь прервал выполнение, то отправляем сообщение об остановке
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        # Если возникла критическая ошибка, то отправляем сообщение об ошибке
        logger.error(f"Критическая ошибка: {str(e)}", exc_info=True)
    finally:
        # Если цикл событий не завершен, то завершаем его
        try:
            # Получаем все задачи, которые еще не завершены
            pending = asyncio.all_tasks(loop)
            # Отменяем все задачи
            for task in pending:
                task.cancel()
            
            # Если есть задачи, которые еще не завершены, то завершаем их
            if pending:
                loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
            
            # Закрываем цикл событий
            loop.close()

        # Если возникла ошибка, то отправляем сообщение об ошибке
        except Exception as e:
            logger.error(f"Ошибка при закрытии цикла событий: {str(e)}", exc_info=True) 

