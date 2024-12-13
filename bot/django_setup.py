import os
import sys
import django

# Получаем путь к директории проекта (на уровень выше от текущего файла)
project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_path)

# Устанавливаем переменную окружения с настройками Django
os.environ['DJANGO_SETTINGS_MODULE'] = 'telereg.settings'

# Инициализируем Django
django.setup() 