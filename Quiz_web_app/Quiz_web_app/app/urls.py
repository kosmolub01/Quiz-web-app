from django.urls import path
from . import views

app_name = 'app'

urlpatterns = [
    # All URLs below start with '/app/'.
    #path('', views.index, name='index'),
    #path('view_schedule/', views.view_schedule, name='view_schedule'),
    #path('change_group/', views.change_group, name='change_group'),
    #path('update_schedules/', views.login_page, name='login_page'),
    path('login/', views.user_login, name='user_login'),
    path('create_account/', views.create_account, name='create_account'),
    path('index/', views.index, name='index'),
    path('select_quiz', views.select_quiz, name='select_quiz'),
    path('solve_quiz/<int:quiz_id>/', views.solve_quiz, name='solve_quiz'),
    path('create_quiz/', views.create_quiz, name='create_quiz'),
    path('quiz_successful_submission/', views.quiz_successful_submission, name='quiz_successful_submission'),
    path('quiz_unsuccessful_submission/', views.quiz_unsuccessful_submission, name='quiz_unsuccessful_submission'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('logout/', views.user_logout, name='user_logout'),
    #path('goodbye/', views.goodbye, name='goodbye'),
    #path('logout_user/', views.logout_user, name='logout_user'),
]
