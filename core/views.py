from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from core.registration_forms import RegisterForm, LoginForm


def signup(request):
    if request.method == "POST":
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password1")
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect("home")
    else:
        form = RegisterForm()
    return render(request, "registration/signup.html", {"form": form})


def signin(request):
    if request.method == "POST":
        form = LoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect("home")
    else:
        form = LoginForm()
    return render(request, "registration/login.html", {"form": form})
