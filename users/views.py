from django.shortcuts import render
from django.views.generic import TemplateView, UpdateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .forms import CustomUserChangeForm
from .models import User

class user_profile(LoginRequiredMixin, UpdateView):
    model = User
    form_class = CustomUserChangeForm
    template_name = 'users/user_profile.html'
    success_url = reverse_lazy('users:profile')

    def get_object(self):
        return self.request.user

class user_management(LoginRequiredMixin, ListView):
    model = User
    template_name = 'users/user_management.html'
    context_object_name = 'users'