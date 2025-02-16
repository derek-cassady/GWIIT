print("DEBUG: Starting to load views for users app...")
from django.shortcuts import render, redirect
from django.http import JsonResponse
from users.authentication import generate_session
from users.authentication import custom_login_required
from django.views.decorators.csrf import csrf_exempt
from .forms import CustomUserChangeForm
from .models import User


# Disable CSRF for simplicity (should be replaced with secure handling)
@csrf_exempt
def login_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required"}, status=400)

    email = request.POST.get("email")
    password = request.POST.get("password")

    try:
        user = User.objects.get(email=email)
        if user.check_password(password):  # Ensure user model has password checking
            session_id = generate_session(user.id)  # Generate Redis session
            response = JsonResponse({"message": "Login successful"})
            response.set_cookie("session_id", session_id, httponly=True, max_age=86400)  # Store session ID in cookie
            return response
    except User.DoesNotExist:
        return JsonResponse({"error": "Invalid credentials"}, status=401)

    return JsonResponse({"error": "Invalid login"}, status=401)

# Handles user profile updates.
@custom_login_required
def user_profile(request):

    user = User.objects.get(id=request.user_id)  # Retrieve user from Redis session

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
