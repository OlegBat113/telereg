from django.db import models
from django.contrib.auth.models import User

# Create your models here.
#Создадим модель для хранения данных Telegram пользователя
class TelegramUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telegram_id = models.CharField(max_length=100, unique=True)
    username = models.CharField(max_length=100, blank=True, null=True)
    auth_token = models.CharField(max_length=100, unique=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.username}"

