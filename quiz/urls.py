from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    
    # Lectures CRUD
    path('lectures/', views.lecture_list, name='lecture_list'),
    path('lectures/add/', views.lecture_create, name='lecture_create'),
    path('lectures/<int:lecture_id>/', views.lecture_detail, name='lecture_detail'),
    path('lectures/<int:lecture_id>/edit/', views.lecture_update, name='lecture_update'),
    path('lectures/<int:lecture_id>/delete/', views.lecture_delete, name='lecture_delete'),
    
    # Questions CRUD
    path('questions/import/', views.question_import, name='question_import'),
    path('questions/add/', views.question_create, name='question_create_generic'),
    path('questions/add/<int:lecture_id>/', views.question_create, name='question_create'),
    path('questions/<int:question_id>/edit/', views.question_update, name='question_update'),
    path('questions/<int:question_id>/delete/', views.question_delete, name='question_delete'),
    
    # Quiz
    path('quiz/all/', views.quiz_start_total, name='quiz_start_total'),
    path('quiz/lecture/<int:lecture_id>/', views.quiz_start_lecture, name='quiz_start_lecture'),
    path('quiz/run/', views.quiz_question, name='quiz_question'),
    path('quiz/summary/', views.quiz_summary, name='quiz_summary'),
]
