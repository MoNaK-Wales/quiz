from django.urls import path
from quiz.views import *


app_name = 'quiz'

urlpatterns = [
    path("start/<int:quiz_id>/", start_quiz, name="start"),
    path("join/", join_quiz, name="join"),
    path("<str:code>/", quiz_room, name="room"),
]