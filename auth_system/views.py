from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import CustomUserCreationForm, ProfileUpdateForm


# Create your views here.
def register(request):
    if request.user.is_authenticated:
        return redirect("browser:home")

    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("browser:home")
    else:
        form = CustomUserCreationForm()

    return render(request, "auth_system/register.html", context={"form": form})


def login_user(request):
    if request.user.is_authenticated:
        return redirect("browser:home")

    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("browser:home")
            else:
                messages.error(request, "Неправильне ім'я користувача або пароль")
    else:
        form = AuthenticationForm()

    return render(request, "auth_system/login.html", context={"form": form})


def logout_user(request):
    if not request.user.is_authenticated:
        return redirect("auth:login")

    logout(request)
    return redirect("browser:home")
