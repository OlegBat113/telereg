from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_page, name='login'),          # Войти через Telegram
    path('generate-telegram-link/', views.generate_telegram_link, name='generate_telegram_link'),   # Генерация ссылки для авторизации
    path('check-auth/', views.check_auth, name='check_auth'), # Проверка статуса авторизации
]
