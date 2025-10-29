from django.shortcuts import render
from quiz.models import Quiz, Question

# Create your views here.
def main_page(request):
    quizzes = Quiz.objects.all().select_related('creator').prefetch_related('questions')
    
    for quiz in quizzes:
        quiz.question_count = quiz.questions.count()
        # quiz.difficulty_color = {
        #     'easy': 'beginner',
        #     'medium': 'intermediate', 
        #     'hard': 'advanced'
        # }.get(quiz.difficulty, 'beginner')
    
    context = {
        'quizzes': quizzes,
        'total_quizzes': Quiz.objects.count(),
        'total_questions': Question.objects.count(),
        'total_completed': 0,
    }
    return render(request, 'browser/main.html', context)

def profile(request):
    user = request.user
    context = {'user': user}
    return render(request, 'browser/profile.html', context)