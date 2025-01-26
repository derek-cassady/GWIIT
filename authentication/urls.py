from django.urls import path
from . import views  # Import the views module from the current app

app_name = 'authentication'

urlpatterns = [
    # Login route
    path('login/', views.login_view(template_name='authentication/login.html'), name='login'),
    # Logout route
    path('logout/', views.logout_view(template_name='authentication/logout.html'), name='logout'),
]