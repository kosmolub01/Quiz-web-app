from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import CustomAuthenticationForm, CustomUserCreationForm, QuizCreationForm
from django.contrib.auth.decorators import login_required
from .models import Quiz, Question, User, Distractor, Answer
from math import ceil
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseRedirect
from time import sleep
#from .quiz_generator import QuizGenerator
from django.db import transaction
import random

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
    Returns a template of index page. It is a quiz selection page.
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
def solve_quiz(request, quiz_id):
    print("in solve_quiz. quiz_id =", quiz_id)

    # Retrieve quiz metadata from DB.
    quiz_metadata = Quiz.objects.get(id=quiz_id)

    # Retrieve all quiz questions from DB.
    questions_metadata = Question.objects.filter(quiz=quiz_id)

    questions = []

    # Needed to evaluate the user answers.
    correct_answers = []

    # Retrieve answer and distractors for each question from DB.
    for quiz_question in questions_metadata:
        correct_answer = Answer.objects.get(question=quiz_question)
        correct_answers.append(correct_answer)
        distractors = Distractor.objects.filter(question=quiz_question)
        answers = [correct_answer]
        answers = answers + list(distractors)
        random.shuffle(answers)

        print("answers", answers)

        questions.append({
                    "question_text": quiz_question.text,
                    "answers": answers,
                })

    # If this is a POST request, we need to evaluate the answers.
    if request.method == "POST":
        print("request.POST:", request.POST)

        selected_answers = {} 
        score = 0

        for key, value in request.POST.items():
                # Retrieve the answers selected by user.
                if key.startswith('question_'):                  
                    question_number = key.split('_')[1]
                    selected_answer = value
                    selected_answers[question_number] = selected_answer

                    # If the answer is correct, add 1 point.
                    if selected_answer == correct_answers[int(question_number)-1].text:
                        score = score + 1
                    else:
                        print(f"selected_answer {selected_answer} is not equal: {correct_answers[int(question_number)-1].text}")

        print(f"Score: {score}")

        return render(request, 'app/result.html')
        

    # If a GET, make sure user did not solve this quiz before and if not, send quiz form.
    else:
        # Prepare the quiz dictionary.
        quiz = {"id": quiz_id,"title": quiz_metadata.title, "description": quiz_metadata.description, "questions": questions}

        # Pass the quiz (questions_metadata, questions) in context.
        context = {'quiz': quiz}

        return render(request, 'app/solve_quiz.html', context)

@login_required
def create_quiz(request):
    # If this is a POST request, we need to process the form data.
    if request.method == "POST":
        # Create a form instance and populate it with data from the request:
        form = QuizCreationForm(request.POST)
        # Check whether it's valid:
        if form.is_valid():
            # Process the data in form.cleaned_data as required - create quiz
            try:
                title = form.cleaned_data['title']
                description = form.cleaned_data['description']
                text = form.cleaned_data['text']

                generate_and_save_quiz(title, description, text)
            except Exception as e:
                print("An error occurred during quiz creation:", e)
                # Redirect to a URL with an error message:
                return HttpResponseRedirect(reverse("app:quiz_unsuccessful_submission"))

            return HttpResponseRedirect(reverse("app:quiz_successful_submission"))

    # If a GET (or any other method), we'll create a blank form.
    else:
        form = QuizCreationForm()

        # Create an HTTP response with the form and set cache control headers
        response = render(request, 'app/create_quiz.html', {"form": form})

        # Set Cache-Control, Pragma, and Expires headers
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'

        return response

@login_required
def quiz_successful_submission(request):
    print("in quiz_successful_submission")
    return render(request, 'app/quiz_successful_submission.html')

@login_required
def quiz_unsuccessful_submission(request):
    print("in quiz_unsuccessful_submission")
    return render(request, 'app/quiz_unsuccessful_submission.html')

@login_required
def leaderboard(request):
    print("in leaderboard")

    # Sort users so the best users are first.
    users = User.objects.all().order_by('score').reverse()

    # Pass quizes to HTML.
    context = {'users': users}

    return render(request, 'app/leaderboard.html', context)

@login_required
def user_logout(request):
    print("in logout")
    logout(request)
    return render(request, 'app/user_logout.html')

def generate_and_save_quiz(title, description, text):

    """with transaction.atomic():
        quiz_generator = QuizGenerator(title, description, text)
        quiz_generator.generate_quiz()
        print(quiz_generator.quiz['title'])

        if len(quiz_generator.quiz['questions']) < 1:
            raise ValidationError("No questions generated for the quiz.") 

        # Save quiz.
        quiz = Quiz.objects.create(
                title=quiz_generator.quiz['title'],
                description=quiz_generator.quiz['description'],
                number_of_questions=len(quiz_generator.quiz['questions'])
            )
        
        # Save the questions.
        for generated_question in quiz_generator.quiz['questions']:
            saved_question = Question.objects.create(
            quiz=quiz,
            text=generated_question['question_text']
            )

            # Save correct answer for the question.
            Answer.objects.create(
                question=saved_question,
                text=generated_question['answer']
            )

            # Save distractors for the question.
            for distractor in generated_question['distractors']:
                Distractor.objects.create(
                question=saved_question,
                text=distractor
                )"""



    