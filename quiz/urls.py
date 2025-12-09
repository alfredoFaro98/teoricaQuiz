from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('subject/<int:subject_id>/', views.subject_detail, name='subject_detail'),
    path('subject/add/', views.subject_create, name='subject_create'),
    path('subject/<int:subject_id>/edit/', views.subject_update, name='subject_update'),
    path('subject/<int:subject_id>/delete/', views.subject_delete, name='subject_delete'),
    
    # Lectures CRUD
    path('lectures/', views.lecture_list, name='lecture_list'),
    path('lectures/add/', views.lecture_create, name='lecture_create'),
    path('lectures/<int:lecture_id>/', views.lecture_detail, name='lecture_detail'),
    path('lectures/<int:lecture_id>/edit/', views.lecture_update, name='lecture_update'),
    path('lectures/<int:lecture_id>/delete/', views.lecture_delete, name='lecture_delete'),
    path('lectures/<int:lecture_id>/edit/', views.lecture_update, name='lecture_update'),
    path('lectures/<int:lecture_id>/delete/', views.lecture_delete, name='lecture_delete'),
    path('lectures/<int:lecture_id>/export/', views.lecture_export_json, name='lecture_export_json'),
    path('api/lectures/', views.api_lectures, name='api_lectures'),
    
    # Questions CRUD
    path('questions/import/', views.question_import, name='question_import'),
    path('questions/add/', views.question_create, name='question_create_generic'),
    path('questions/add/<int:lecture_id>/', views.question_create, name='question_create'),
    path('questions/<int:question_id>/edit/', views.question_update, name='question_update'),
    path('questions/<int:question_id>/delete/', views.question_delete, name='question_delete'),
    
    # Quiz
    path('quiz/all/', views.quiz_start_total, name='quiz_start_total'),
    path('quiz/subject/<int:subject_id>/', views.quiz_start_subject, name='quiz_start_subject'),
    path('quiz/lecture/<int:lecture_id>/', views.quiz_start_lecture, name='quiz_start_lecture'),
    path('quiz/run/', views.quiz_question, name='quiz_question'),
    path('quiz/summary/', views.quiz_summary, name='quiz_summary'),
    
    # Stats
    path('stats/', views.stats_global, name='stats_global'),
]
