from django import forms
from django.forms import ModelForm, Form
from quiz.models import Quiz, Question, Answer
import os

class QuizForm(ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'description', 'is_public']
        # fields = ['title', 'description', 'cover', 'is_public']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Quiz title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Quiz description', 'rows': 3}),
            # 'cover': forms.ClearableFileInput(attrs={'class': 'form-control-file', 'accept': 'image/*'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
class QuestionForm(ModelForm):
    # media = forms.FileField(
    #     required=False,
    #     widget=forms.ClearableFileInput(attrs={'class': 'form-control-file', 'accept': 'image/*,video/*'})
    # )

    class Meta:
        model = Question
        fields = ['text', 'time_limit']
        widgets = {
            'text': forms.TextInput(attrs={'class': 'form-control question-text', 'placeholder': 'Question text'}),
            'time_limit': forms.NumberInput(attrs={
                'class': 'form-control time-limit',
                'min': 5, 
                'max': 120, 
                'step': 5, 
                'value': 30
            }),
        }

    # def clean(self):
    #     cleaned = super().clean()
    #     media = cleaned.get('media')

    #     if media:
    #         ext = os.path.splitext(media.name)[1].lower()
    #         if ext in ['.jpg', '.jpeg', '.png', '.gif', '.svg']:
    #             cleaned['image'] = media
    #             cleaned['video'] = None
    #         elif ext in ['.mp4']:
    #             cleaned['video'] = media
    #             cleaned['image'] = None
    #         else:
    #             raise forms.ValidationError("Unsupported file type. Please upload an image (.jpg, .jpeg, .png, .gif, .svg) or a video (.mp4).")
        
    #     return cleaned

    # def save(self, commit=True):
    #     instance = super().save(commit=False)
    #     media = self.cleaned_data.get('media')

    #     if media:
    #         ext = os.path.splitext(media.name)[1].lower()
    #         if ext in ['.jpg', '.jpeg', '.png', '.gif', '.svg']:
    #             instance.image = media
    #             instance.video = None
    #         elif ext in ['.mp4']:
    #             instance.video = media
    #             instance.image = None

    #     if commit:
    #         instance.save()

    #     return instance


class AnswerForm(Form):
    A = forms.CharField(max_length=200, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Option A'}))
    B = forms.CharField(max_length=200, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Option B'}))
    C = forms.CharField(max_length=200, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Option C'}))
    D = forms.CharField(max_length=200, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Option D'}))
    correct_option = forms.ChoiceField(
        choices=[("A", "A"), ("B", "B"), ("C", "C"), ("D", "D")],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )