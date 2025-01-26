from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
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