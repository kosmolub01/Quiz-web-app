from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import CustomAuthenticationForm, CustomUserCreationForm

def user_login(request):
    print("in login")
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect(reverse('app:index'))  # Redirect to the home page or any desired URL
        else:
            print("Form errors:", form.errors)
    else:
        form = CustomAuthenticationForm()
    return render(request, 'app/login.html', {'form': form})

def create_account(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            print("valid")
            user = form.save()
            login(request, user)
            return redirect(reverse('app:index'))  # Redirect to the home page or any desired URL
        else:
            print("Form errors:", form.errors)
    else:
        form = CustomUserCreationForm()
    return render(request, 'app/create_account.html', {'form': form})

def index(request):
    print("in index")
    return render(request, 'app/index.html')

def solve_test(request):
    print("in logout")
    return render(request, 'app/index.html')

def create_test(request):
    print("in create_test")
    return render(request, 'app/index.html')

def ranking(request):
    print("in ranking")
    return render(request, 'app/index.html')

def logout(request):
    print("in logout")
    return render(request, 'app/index.html')
