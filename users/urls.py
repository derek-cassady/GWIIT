print("DEBUG: Starting to load URLs for users app...")
from django.urls import path
from . import views

app_name = 'users'
urlpatterns = []

# urlpatterns = [
#     path('profile/', views.user_profile, name='user_profile'),
#     path('admin/users/', views.user_management, name='user_management'),
# ]

print("DEBUG: Finished loading URLs for users app.")