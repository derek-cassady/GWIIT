from django.shortcuts import render

def homepage(request):
    return render(request, 'authentication/templates/authentication/login.html')