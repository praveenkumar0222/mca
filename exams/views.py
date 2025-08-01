from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone

from .models import TestAttempt, Question, Answer, UserAnswer
from .models import (
    ExamType, Subject, Chapter, Question, Answer, 
    MockTest, UserAnswer, TestAttempt
)
from .forms import (
    ExamTypeForm, SubjectForm, ChapterForm,
    QuestionForm, AnswerForm, MockTestForm
)
from django.forms import inlineformset_factory
from django.db.models import Count

@login_required
def exam_types(request):
    exam_types = ExamType.objects.annotate(
        subject_count=Count('subject'),
        mock_test_count=Count('mocktest')
    )
    return render(request, 'exams/exam_types.html', {'exam_types': exam_types})

@login_required
def subjects(request, exam_type_id):
    exam_type = get_object_or_404(ExamType, pk=exam_type_id)
    subjects = Subject.objects.filter(exam_type=exam_type).annotate(
        chapter_count=Count('chapter'),
        question_count=Count('question')
    )
    return render(request, 'exams/subjects.html', {
        'exam_type': exam_type,
        'subjects': subjects
    })

@login_required
def chapters(request, subject_id):
    subject = get_object_or_404(Subject, pk=subject_id)
    chapters = Chapter.objects.filter(subject=subject).annotate(
        question_count=Count('question')
    )
    return render(request, 'exams/chapters.html', {
        'subject': subject,
        'chapters': chapters
    })

@login_required
def mock_tests(request, exam_type_id):
    exam_type = get_object_or_404(ExamType, pk=exam_type_id)
    mock_tests = MockTest.objects.filter(exam_type=exam_type)
    return render(request, 'exams/mock_tests.html', {
        'exam_type': exam_type,
        'mock_tests': mock_tests
    })

@login_required
def start_mock_test(request, mock_test_id):
    mock_test = get_object_or_404(MockTest, pk=mock_test_id)
    attempt = TestAttempt.objects.create(
        user=request.user,
        mock_test=mock_test,
        total_questions=mock_test.questions.count()
    )
    return redirect('take_test', attempt_id=attempt.id)

@login_required
def start_subject_test(request, subject_id):
    subject = get_object_or_404(Subject, pk=subject_id)
    questions = Question.objects.filter(subject=subject)
    attempt = TestAttempt.objects.create(
        user=request.user,
        subject=subject,
        total_questions=questions.count()
    )
    return redirect('take_test', attempt_id=attempt.id)

@login_required
def start_chapter_test(request, chapter_id):
    chapter = get_object_or_404(Chapter, pk=chapter_id)
    questions = Question.objects.filter(chapter=chapter)
    attempt = TestAttempt.objects.create(
        user=request.user,
        chapter=chapter,
        total_questions=questions.count()
    )
    return redirect('take_test', attempt_id=attempt.id)




@login_required
def take_test(request, attempt_id):
    attempt = get_object_or_404(TestAttempt, pk=attempt_id, user=request.user)
    
    # Get questions based on attempt type
    if attempt.mock_test:
        questions = list(attempt.mock_test.questions.all().order_by('id'))
    elif attempt.subject:
        questions = list(Question.objects.filter(subject=attempt.subject).order_by('id'))
    elif attempt.chapter:
        questions = list(Question.objects.filter(chapter=attempt.chapter).order_by('id'))
    else:
        questions = []
    
    # Get all user answers for this attempt
    user_answers = UserAnswer.objects.filter(
        user=request.user,
        question__in=[q.id for q in questions]
    ).select_related('selected_answer')
    
    # Create a dictionary of {question_id: selected_answer_id}
    user_answers_dict = {ua.question.id: ua.selected_answer.id for ua in user_answers}
    
    # Handle answer submission
    if request.method == 'POST':
        answer_id = request.POST.get('answer')
        question_id = request.POST.get('question_id')
        
        if answer_id and question_id:
            question = get_object_or_404(Question, pk=question_id)
            selected_answer = get_object_or_404(Answer, pk=answer_id)
            is_correct = selected_answer.is_correct
            
            # Save user's answer
            UserAnswer.objects.update_or_create(
                user=request.user,
                question=question,
                defaults={
                    'selected_answer': selected_answer,
                    'is_correct': is_correct
                }
            )
            
            # Update the user_answers_dict
            user_answers_dict[question.id] = selected_answer.id
            
            # Update score if correct
            if is_correct:
                attempt.score += question.marks
                attempt.save()
            
            # Get correct answer
            correct_answer = question.answers.filter(is_correct=True).first()
            
            return JsonResponse({
                'is_correct': is_correct,
                'correct_answer_id': correct_answer.id if correct_answer else None,
            })
    
    # Handle question navigation
    if request.method == 'GET' and 'question' in request.GET:
        question_index = int(request.GET.get('question')) - 1
        if 0 <= question_index < len(questions):
            attempt.current_question_index = question_index
            attempt.save()
    
    # Get current question
    current_question = None
    selected_answer_id = None
    if questions and 0 <= attempt.current_question_index < len(questions):
        current_question = questions[attempt.current_question_index]
        selected_answer_id = user_answers_dict.get(current_question.id)
    
    # Calculate progress
    progress = {
        'current': attempt.current_question_index + 1,
        'total': len(questions),
        'has_previous': attempt.current_question_index > 0,
        'has_next': attempt.current_question_index < len(questions) - 1,
        'question_range': range(1, len(questions) + 1),
        'answered_questions': [i+1 for i, q in enumerate(questions) if q.id in user_answers_dict],
    }
    
    return render(request, 'exams/take_test.html', {
        'attempt': attempt,
        'question': current_question,
        'progress': progress,
        'selected_answer_id': selected_answer_id,
        'user_answers_dict': user_answers_dict,  # Pass the dictionary to template
    })



@login_required
def test_result(request, attempt_id):
    attempt = get_object_or_404(TestAttempt, pk=attempt_id, user=request.user)
    
    if attempt.mock_test:
        questions = attempt.mock_test.questions.all()
    elif attempt.subject:
        questions = Question.objects.filter(subject=attempt.subject)
    elif attempt.chapter:
        questions = Question.objects.filter(chapter=attempt.chapter)
    else:
        questions = Question.objects.none()
    
    user_answers = UserAnswer.objects.filter(
        user=request.user,
        question__in=questions
    ).select_related('question', 'selected_answer')
    
    return render(request, 'exams/test_result.html', {
        'attempt': attempt,
        'user_answers': user_answers,
    })

@login_required
def test_history(request):
    attempts = TestAttempt.objects.filter(user=request.user).order_by('-start_time')
    return render(request, 'exams/test_history.html', {'attempts': attempts})

# Admin views for managing content
@login_required
def add_question(request):
    AnswerFormSet = inlineformset_factory(
        Question, Answer, form=AnswerForm, extra=4, max_num=4, min_num=1
    )
    
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        formset = AnswerFormSet(request.POST)
        
        if form.is_valid() and formset.is_valid():
            question = form.save()
            formset.instance = question
            formset.save()
            return redirect('add_question')
    else:
        form = QuestionForm()
        formset = AnswerFormSet()
    
    return render(request, 'exams/add_question.html', {
        'form': form,
        'formset': formset
    })

@login_required
def add_mock_test(request):
    if request.method == 'POST':
        form = MockTestForm(request.POST)
        if form.is_valid():
            mock_test = form.save()
            return redirect('manage_mock_test', mock_test_id=mock_test.id)
    else:
        form = MockTestForm()
    
    return render(request, 'exams/add_mock_test.html', {'form': form})

@login_required
def manage_mock_test(request, mock_test_id):
    mock_test = get_object_or_404(MockTest, pk=mock_test_id)
    questions = Question.objects.filter(exam_type=mock_test.exam_type)
    
    if request.method == 'POST':
        selected_questions = request.POST.getlist('questions')
        mock_test.questions.set(selected_questions)
        return redirect('mock_tests', exam_type_id=mock_test.exam_type.id)
    
    return render(request, 'exams/manage_mock_test.html', {
        'mock_test': mock_test,
        'questions': questions,
        'selected_questions': mock_test.questions.values_list('id', flat=True)
    })