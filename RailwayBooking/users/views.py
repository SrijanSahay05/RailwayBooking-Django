from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from .forms import CustomUserLoginForm, CustomUserCreationForm


def login_view(request):
    if request.method == "POST":
        form = CustomUserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("useranme")
            password = form.cleaned_data.get("password")
            user = autehnticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("index")
    else:
        form = CustomUserLoginForm()
    return render(request, "users/login.html", {"form": form})


def register_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("index")
    else:
        form = CustomUserCreationForm()

    return render(request, "users/register.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("index")
