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
    path('solve_test/', views.solve_test, name='solve_test'),
    path('create_test/', views.create_test, name='create_test'),
    path('ranking/', views.ranking, name='ranking'),
    path('logout/', views.logout, name='logout'),
    #path('logout_user/', views.logout_user, name='logout_user'),
]
