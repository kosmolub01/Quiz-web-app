from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import CustomAuthenticationForm, CustomUserCreationForm
from django.contrib.auth.decorators import login_required

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
    return render(request, 'app/user_login.html', {'form': form})

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

@login_required
def index(request):
    print("in index")
    return render(request, 'app/index.html')

@login_required
def solve_test(request):
    print("in logout")
    return render(request, 'app/index.html')

@login_required
def create_test(request):
    print("in create_test")
    return render(request, 'app/index.html')

@login_required
def ranking(request):
    print("in ranking")
    return render(request, 'app/index.html')

@login_required
def user_logout(request):
    print("in logout")
    logout(request)
    return render(request, 'app/user_logout.html')
