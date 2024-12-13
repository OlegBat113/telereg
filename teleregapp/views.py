from django.shortcuts import render, redirect
from django.contrib.auth import login, logout as auth_logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from .models import TelegramUser
import uuid
from django.conf import settings
import logging

logger = logging.getLogger('teleregapp')

# Create your views here.

# Главная страница
def index(request):
    logger.info(f"-> index() ...")
    # Отображаем Главную страницу
    return render(request, 'teleregapp/index.html')


#Создадим views для авторизации:
def login_page(request):
    logger.info(f"-> login_page() ...")
    logger.info(f"Пользователь {request.user} зашел на страницу входа")
    context = {
        'is_authenticated': request.user.is_authenticated,
    }
    # Отображаем страницу авторизации
    return render(request, 'teleregapp/login.html', context)


# Генерация ссылки для авторизации
def generate_telegram_link(request):
    logger.info(f"-> generate_telegram_link() ...")
    # Генерируем уникальный токен
    token = str(uuid.uuid4())
    # Сохраняем токен в сессии
    request.session['auth_token'] = token
    logger.info(f"Сгенерирован новый токен авторизации: {token}")
    # Формируем ссылку для перенаправления в Telegram
    bot_link = f"https://t.me/{settings.TELEGRAM_BOT_USERNAME}?start={token}"
    # Перенаправляем пользователя на бот
    return redirect(bot_link)


# Проверка статуса авторизации
def check_auth(request):
    logger.info(f"-> check_auth() ...")
    # Проверяем, есть ли токен в сессии
    token = request.session.get('auth_token')
    logger.info(f"Токен авторизации: {token}")

    if token:
        try:
            # Получаем пользователя по токену
            telegram_user = TelegramUser.objects.get(auth_token=token)
            # Авторизуем пользователя в Django
            login(request, telegram_user.user)
            logger.info(f"Успешная авторизация пользователя {telegram_user.username}")
            # Возвращаем JSON с информацией о статусе авторизации
            return JsonResponse({
                'authenticated': True, 
                'username': telegram_user.username
            })
        except TelegramUser.DoesNotExist:
            # Если пользователя нет, то возвращаем False
            logger.warning(f"Попытка авторизации с несуществующим токеном: {token}")
            return JsonResponse({'authenticated': False})

    # Если токена нет, то возвращаем False
    logger.warning("Попытка проверки авторизации без токена")
    return JsonResponse({'authenticated': False})

# Выход из системы
def logout(request):
    logger.info(f"-> logout() ...")
    logger.info(f"Пользователь {request.user} вышел из системы")
    auth_logout(request)
    return redirect('/')
