print("DEBUG: Starting to load views for authorization app...")
from django.shortcuts import render

def roles_view(request):
    # Add any logic needed for rendering the roles page.
    return render(request, 'authorization/roles.html')

def permissions_view(request):
    # Add any logic needed for rendering the permissions page.
    return render(request, 'authorization/permissions.html')

print("DEBUG: Finished loading views for authorization app.")