# exams/forms.py
from django import forms
from .models import ExamType, Subject, Chapter, Question, Answer, MockTest

class ExamTypeForm(forms.ModelForm):
    class Meta:
        model = ExamType
        fields = ['name', 'description']

class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['exam_type', 'name', 'description']

class ChapterForm(forms.ModelForm):
    class Meta:
        model = Chapter
        fields = ['subject', 'name', 'description']

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['exam_type', 'subject', 'chapter', 'question_type', 'text', 'marks', 'difficulty', 'explanation']

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['text', 'is_correct']

AnswerFormSet = forms.inlineformset_factory(
    Question, Answer, form=AnswerForm, extra=4, max_num=4, min_num=1
)

class MockTestForm(forms.ModelForm):
    class Meta:
        model = MockTest
        fields = ['exam_type', 'title', 'description', 'duration', 'total_marks']