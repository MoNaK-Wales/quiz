from django.db import models
import random
import string

# Create your models here.
class Quiz(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    cover = models.ImageField(upload_to='quiz_covers/', null=True, blank=True)
    creator = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, related_name='quizzes')
    created_at = models.DateTimeField(auto_now_add=True)
    is_public = models.BooleanField(default=True)
    play_count = models.IntegerField(default=0)

    def __str__(self):
        return self.title


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    image = models.ImageField(upload_to='questions/', null=True, blank=True)
    video = models.FileField(upload_to='questions/', null=True, blank=True)
    time_limit = models.IntegerField(default=30)

    def __str__(self):
        return self.text[:50]


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)
    option_char = models.CharField(
        max_length=1, choices=[("A", "A"), ("B", "B"), ("C", "C"), ("D", "D")]
    )

    def __str__(self):
        return f"({self.option_char}) {self.text}"


class QuizSession(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='sessions')
    code = models.CharField(max_length=6, unique=True)
    current_question_index = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        super().save(*args, **kwargs)