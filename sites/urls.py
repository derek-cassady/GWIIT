from django.urls import path
from . import views  # Import views from the current app

app_name = 'sites'

urlpatterns = [
    # Example route for site listing
    path('', views.site_list, name='site_list'),
    # Example route for viewing a specific site
    path('<int:pk>/', views.site_detail, name='site_detail'),
]