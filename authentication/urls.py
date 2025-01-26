from django.urls import path
from . import views  # Import the views module from the current app

app_name = 'authentication'

urlpatterns = [
    # Login route
    path('login/', views.login_view(template_name='users/login.html'), name='login'),
    # Logout route
    path('logout/', views.logout_view(template_name='users/logout.html'), name='logout'),
]