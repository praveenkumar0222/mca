from django.urls import path
from . import views

urlpatterns = [
    path('', views.exam_types, name='exam_types'),
    path('subjects/<int:exam_type_id>/', views.subjects, name='subjects'),
    path('chapters/<int:subject_id>/', views.chapters, name='chapters'),
    path('mock_tests/<int:exam_type_id>/', views.mock_tests, name='mock_tests'),
    
    path('start_mock_test/<int:mock_test_id>/', views.start_mock_test, name='start_mock_test'),
    path('start_subject_test/<int:subject_id>/', views.start_subject_test, name='start_subject_test'),
    path('start_chapter_test/<int:chapter_id>/', views.start_chapter_test, name='start_chapter_test'),
    
    path('take_test/<int:attempt_id>/', views.take_test, name='take_test'),
    path('test_result/<int:attempt_id>/', views.test_result, name='test_result'),
    path('test_history/', views.test_history, name='test_history'),
    
    path('add_question/', views.add_question, name='add_question'),
    path('add_mock_test/', views.add_mock_test, name='add_mock_test'),
    path('manage_mock_test/<int:mock_test_id>/', views.manage_mock_test, name='manage_mock_test'),
]