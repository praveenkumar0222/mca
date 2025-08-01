# exams/admin.py
from django.contrib import admin
from .models import (
    ExamType, Subject, Chapter,
    Question, Answer, MockTest,
    UserAnswer, TestAttempt
)

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 4

class QuestionAdmin(admin.ModelAdmin):
    inlines = [AnswerInline]
    list_display = ('text', 'exam_type', 'subject', 'chapter', 'question_type', 'difficulty')
    list_filter = ('exam_type', 'subject', 'chapter', 'question_type', 'difficulty')
    search_fields = ('text',)

class MockTestAdmin(admin.ModelAdmin):
    filter_horizontal = ('questions',)
    list_display = ('title', 'exam_type', 'duration', 'total_marks')
    list_filter = ('exam_type',)

admin.site.register(ExamType)
admin.site.register(Subject)
admin.site.register(Chapter)
admin.site.register(Question, QuestionAdmin)
admin.site.register(MockTest, MockTestAdmin)
admin.site.register(UserAnswer)
admin.site.register(TestAttempt)