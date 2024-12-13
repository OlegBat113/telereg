# Импортируем библиотеку models из библиотеки django.db
from django.db import models
# Импортируем класс User из библиотеки django.contrib.auth.models
from django.contrib.auth.models import User

#Создадим модель для хранения данных Telegram пользователя
class TelegramUser(models.Model):
    # Создаем связь один к одному с моделью User
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Создаем поле для хранения ID Telegram пользователя
    telegram_id = models.CharField(max_length=100, unique=True)
    # Создаем поле для хранения username Telegram пользователя
    username = models.CharField(max_length=100, blank=True, null=True)
    # Создаем поле для хранения токена
    auth_token = models.CharField(max_length=100, unique=True, null=True)

    # Создаем метод для отображения строкового представления объекта
    def __str__(self):
        return f"{self.telegram_id} - {self.username}"

