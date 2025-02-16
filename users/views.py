print("DEBUG: Starting to load views for users app...")
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, UpdateView, ListView
from django.urls import reverse_lazy
from .forms import CustomUserChangeForm
from .models import User
from users.authentication import CustomLoginRequiredMixin, custom_login_required

# Handles user profile updates.
@custom_login_required
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

# Displays user management dashboard.
@custom_login_required
def user_management(request):

    users = User.objects.all()
    return render(request, 'users/user_management.html', {'users': users})

print("DEBUG: Finished loading views for users app.")
