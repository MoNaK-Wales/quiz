from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.forms import formset_factory, BaseFormSet
from browser.forms import QuizForm, QuestionForm, AnswerForm
from quiz.models import Quiz, Question, Answer
from typing import cast

# Create your views here.
def main_page(request):
    quizzes = Quiz.objects.all().select_related('creator').prefetch_related('questions')
    
    for quiz in quizzes:
        quiz.question_count = quiz.questions.count()
    
    context = {
        'quizzes': quizzes,
        'total_quizzes': Quiz.objects.count(),
        'total_questions': Question.objects.count(),
        'total_completed': 0,
    }
    return render(request, 'browser/main.html', context)

@login_required
def profile(request):
    user = request.user
    # 1. Достаем квизы только этого юзера
    user_quizzes = Quiz.objects.filter(creator=user).prefetch_related('questions')
    
    # 2. Считаем вопросы (как ты делал на главной)
    for quiz in user_quizzes:
        quiz.question_count = quiz.questions.count()

    context = {
        'user': user,
        'user_quizzes': user_quizzes # <-- Теперь шаблон их увидит
    }
    return render(request, 'browser/profile.html', context)

@login_required
def delete_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    if quiz.creator == request.user or request.user.is_staff:
        quiz.delete()
    
    return redirect(request.META.get('HTTP_REFERER', 'browser:main_page'))

class QuizFormView(LoginRequiredMixin, FormView):
    template_name = 'browser/quiz_form.html'
    success_url = '/'
    form_class = QuizForm

    QuestionFormSet = formset_factory(QuestionForm, can_delete=True)
    AnswerFormSet = formset_factory(AnswerForm)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['quiz_form'] = context.get('quiz_form', self.form_class())
        context['question_formset'] = self.QuestionFormSet(prefix='questions')
        context['answer_formset'] = self.AnswerFormSet(prefix='answers')
        context['form_pairs'] = zip(context['question_formset'], context['answer_formset'])
        return context

    def post(self, request, *args, **kwargs):
        quiz_form = QuizForm(request.POST, request.FILES)
        question_formset = self.QuestionFormSet(request.POST, request.FILES, prefix='questions')
        answer_formset = self.AnswerFormSet(request.POST, prefix='answers')

        if all([quiz_form.is_valid(), question_formset.is_valid(), answer_formset.is_valid()]):
            return self.form_valid(quiz_form, question_formset, answer_formset)
        else:
            return self.form_invalid(quiz_form, question_formset, answer_formset)
    
    def form_valid(self, quiz_form: QuizForm, question_formset: BaseFormSet, answer_formset: BaseFormSet):
        quiz = quiz_form.save(commit=False)
        quiz.creator = self.request.user
        quiz.save()

        for question_form, answer_form in zip(question_formset, answer_formset):
            q_form = cast(QuestionForm, question_form)
            a_form = cast(AnswerForm, answer_form)

            if not q_form.cleaned_data:
                continue
            
            if q_form.cleaned_data.get('DELETE'):
                continue

            question = question_form.save(commit=False)
            question.quiz = quiz
            question.save()

            answers = a_form.cleaned_data
            correct_answer = answers.get('correct_option')

            for option_char in ['A', 'B', 'C', 'D']:
                Answer.objects.create(
                    question=question,
                    text=answers.get(option_char),
                    is_correct=(option_char == correct_answer),
                    option_char=option_char
                )
            
        return redirect(self.success_url)
    
    def form_invalid(self, quiz_form, question_formset, answer_formset):
        context = self.get_context_data()
        context['quiz_form'] = quiz_form
        context['question_formset'] = question_formset
        context['answer_formset'] = answer_formset
        return render(self.request, self.template_name, context)
