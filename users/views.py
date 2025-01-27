from django.shortcuts import render, redirect
from django.views.generic import TemplateView, UpdateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from .forms import CustomUserChangeForm
from .models import User

@login_required
def user_profile(request):
    user = request.user
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('users:user_profile')
    else:
        form = CustomUserChangeForm(instance=user)
    return render(request, 'users/user_profile.html', {'form': form})

@login_required
def user_management(request):
    users = User.objects.all()
    return render(request, 'users/user_management.html', {'users': users})