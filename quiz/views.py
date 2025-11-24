from django.shortcuts import render, get_object_or_404, redirect
from .models import Quiz, QuizSession


# Create your views here.
def start_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    session = QuizSession.objects.create(quiz=quiz)

    return render(request, "quiz/start.html", {"quiz": quiz, "session": session})


def join_quiz(request):
    if request.method == "POST":
        code = request.POST.get("code")
        name = request.POST.get("name")

        if not name or not code:
            return render(request, "quiz/join.html", {'error': 'Enter both name and code'})

        try:
            session = get_object_or_404(QuizSession, code=code, is_active=True)
            request.session['player_name'] = name
            return redirect("quiz:room", code=session.code)
        except QuizSession.DoesNotExist:
            return render(request, "quiz/join.html", {'error': 'Code was not found'})

    return render(request, "quiz/join.html")


def quiz_room(request, code):
    session = get_object_or_404(QuizSession, code=code)
    player_name = request.session.get('player_name')
    return render(request, "quiz/room.html", {"session": session, 'player_name': player_name})
