print("DEBUG: Starting to load URLs for authorization app...")
from django.urls import path
from . import views  # Import your custom views module

app_name = 'authorization'

urlpatterns = [
    # Route for managing roles
    path('roles/', views.roles_view, name='roles'),
    # Route for managing permissions
    path('permissions/', views.permissions_view, name='permissions'),
]

print("DEBUG: Finished loading URLs for authorization app.")