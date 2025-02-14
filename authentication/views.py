print("DEBUG: Starting to load views for authentication app...")
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Replace with the appropriate success URL
            return redirect("some_success_url")
        else:
            return HttpResponse("Invalid login")
    return render(request, "authentication/login.html")

def logout_view(request):
    # Logs out the current user
    logout(request)
    # Redirect to the login page after logout
    return redirect('authentication:login')

print("DEBUG: Finished loading views for authentication app.")