from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('profile/', views.user_profile, name='user_profile'),
    path('admin/users/', views.user_management, name='user_management'),
]