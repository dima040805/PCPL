from django.contrib import admin
from django.urls import path
from games import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('get-games/', views.get_games, name='get_games'),
    path('login/', views.steam_login, name='steam_login'),
    path('login/callback/', views.steam_callback, name='steam_callback'),
    path('profile/<str:steam_id>/', views.profile_page, name='profile')
]
