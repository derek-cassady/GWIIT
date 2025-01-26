from django.urls import path
from . import views  # Import views from the current app

app_name = 'organizations'

urlpatterns = [
    # Example route for organization listing
    path('', views.organization_list, name='organization_list'),
    # Example route for viewing a specific organization
    path('<int:pk>/', views.organization_detail, name='organization_detail'),
]