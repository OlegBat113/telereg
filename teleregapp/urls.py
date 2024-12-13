from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_page, name='login_page'),
    path('generate-link/', views.generate_telegram_link, name='generate_telegram_link'),
    path('check-auth/', views.check_auth, name='check_auth'),
    path('logout/', views.logout, name='logout'),
]
