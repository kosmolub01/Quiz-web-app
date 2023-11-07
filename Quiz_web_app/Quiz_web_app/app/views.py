from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import CustomAuthenticationForm, CustomUserCreationForm
from django.contrib.auth.decorators import login_required
from .models import Quiz, User
from math import ceil
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

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
    """
    Returns a template of index pages. It is a quiz selection page.
    You can also navigate to other pages.
    """
    print("in index")

    # Get number of quizzes to determine the number of pages to show in quiz selection section.
    number_of_quizzes = Quiz.objects.count()

    # 4 quizzes per page.
    range_of_pages = range(1, ceil(number_of_quizzes / 4 + 1))

    # Pass number of quizes to HTML.
    context = {'range_of_pages': range_of_pages}

    return render(request, 'app/index.html', context)

@login_required
def select_quiz(request):
    """
    Returns a template of quiz selection section. It is a part of index page.
    Depending on requested number of pages, it returns proper quizzes.
    """

    print("in select_quiz")

    # Select quizzes from proper pages. Get the page number from the request.

    # Explicitly ordering by primary key to get rid of the warning.
    quizzes_all = Quiz.objects.all().order_by('id')  

    # Show 4 items per page.
    paginator = Paginator(quizzes_all, 4)  

    page = request.GET.get('page')

    try:
        # Get the page.
        quizzes = paginator.page(page)
    except PageNotAnInteger:
        # Get the first page.
        quizzes = paginator.page(1)
    except EmptyPage:
        # Get the last page.
        quizzes = paginator.page(paginator.num_pages)

    # Pass quizes to HTML.
    context = {'quizzes': quizzes}

    return render(request, 'app/select_quiz.html', context)

@login_required
def solve_test(request):
    print("in logout")
    return render(request, 'app/index.html')

@login_required
def create_test(request):
    print("in create_test")
    return render(request, 'app/index.html')

@login_required
def leaderboard(request):
    print("in leaderboard")

    # Sort users so the best users are first.
    users = User.objects.all().order_by('score')  

    # Pass quizes to HTML.
    context = {'users': users}

    return render(request, 'app/leaderboard.html', context)

@login_required
def user_logout(request):
    print("in logout")
    logout(request)
    return render(request, 'app/user_logout.html')
