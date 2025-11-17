from django.urls import path
from browser.views import *


app_name = 'browser'

urlpatterns = [
    path('', main_page, name='home'),
    path('profile/', profile, name='profile'),
    path('create-quiz/', QuizFormView.as_view(), name='create_quiz'),
]