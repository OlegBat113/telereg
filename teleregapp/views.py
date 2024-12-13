from django.shortcuts import render, redirect
from django.contrib.auth import login
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
    context = {
        'products': ['Товар 1', 'Товар 2', 'Товар 3'],
    }
    return render(request, 'teleregapp/index.html', context)


#Создадим views для авторизации:
def login_page(request):
    logger.info(f"Пользователь {request.user} зашел на страницу входа")
    context = {
        'is_authenticated': request.user.is_authenticated,
    }
    return render(request, 'teleregapp/login.html', context)


# Генерация ссылки для авторизации
def generate_telegram_link(request):
    token = str(uuid.uuid4())
    request.session['auth_token'] = token
    logger.info(f"Сгенерирован новый токен авторизации: {token}")
    bot_link = f"https://t.me/{settings.TELEGRAM_BOT_USERNAME}?start={token}"
    return redirect(bot_link)


# Проверка статуса авторизации
def check_auth(request):
    token = request.session.get('auth_token')
    if token:
        try:
            telegram_user = TelegramUser.objects.get(auth_token=token)
            login(request, telegram_user.user)
            logger.info(f"Успешная авторизация пользователя {telegram_user.username}")
            return JsonResponse({
                'authenticated': True, 
                'username': telegram_user.username
            })
        except TelegramUser.DoesNotExist:
            logger.warning(f"Попытка авторизации с несуществующим токеном: {token}")
            return JsonResponse({'authenticated': False})
    logger.warning("Попытка проверки авторизации без токена")
    return JsonResponse({'authenticated': False})
