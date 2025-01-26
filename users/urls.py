from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'users'

urlpatterns = [
    path('profile/', views.profile_view, name='user_profile'),
    path('admin/users/', views.user_management_view, name='user_management'),
]