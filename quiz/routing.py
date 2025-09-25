from django.urls import re_path
from quiz.consumers import QuizConsumer


# Типа urls.py, но для вебсокетов, ссылка используется в джаваскрипте (передаётся в config/asgi.py)
websocket_urlpatterns = [
    re_path(r'^ws/quiz/(?P<quiz_id>\d+)/$', QuizConsumer.as_asgi()),
    re_path(r'^ws/test/$', QuizConsumer.as_asgi()),
]