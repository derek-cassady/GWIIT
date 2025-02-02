from django.shortcuts import render, redirect
from django.contrib.auth import logout

def homepage(request):
    """Render the login page as the homepage."""
    return render(request, 'authentication/login.html')

def logout_view(request):
    """Logs the user out and redirects to the login page."""
    logout(request)
    return redirect('homepage')

def authentication_view(request):
    """Placeholder for authentication dashboard or main page."""
    return render(request, 'authentication/dashboard.html')

def authorization_view(request):
    """Placeholder for authorization settings or main page."""
    return render(request, 'authorization/dashboard.html')

def organizations_view(request):
    """Placeholder for organization management page."""
    return render(request, 'organizations/organization_list.html')

def sites_view(request):
    """Placeholder for site management page."""
    return render(request, 'sites/site_list.html')

def users_view(request):
    """Placeholder for user management page."""
    return render(request, 'users/user_list.html')