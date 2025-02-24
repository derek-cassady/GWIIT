print("DEBUG: Starting to load URLs for organizations app...")

from django.urls import path
# Import views from the current app
from . import views

app_name = 'organizations'
urlpatterns = []
# urlpatterns = [
#     # Example route for organization listing
#     # empty string '' means this view handles 'organizations/' directly
#     path('', views.organization_list, name='organization_list'),
    
#     # Example route for viewing a specific organization
#     path('<int:pk>/', views.organization_detail, name='organization_detail'),

#     # OrganizationType management (add) route
#     path('types/manage/', views.organization_type_manage, name='organization_type_manage'),

#     # OrganizationType details route
#     path('types/edit/<int:pk>/', views.get_organization_type_details, name='get_organization_type_details'),
    
#     # OrganizationType description route
#     path('type-description/', views.get_organization_type_description, name='type_description'),

#     # OrganizationType edit route
#     path('types/edit/<int:pk>/', views.edit_organization_type, name='edit_organization_type'),

#     # OrganizationType delete route
#     path('types/delete/<int:pk>/', views.delete_organization_type, name='delete_organization_type'),
# ]

print("DEBUG: Finished loading URLs for organizations app.")