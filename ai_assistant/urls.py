from django.urls import path
from . import views

urlpatterns = [
    # Web views
    path('', views.AIAssistantHomeView.as_view(), name='ai_assistant_home'),
    path('symptoms/', views.SymptomOrganizerView.as_view(), name='ai_symptom_organizer'),
    path('questions/', views.QuestionGeneratorView.as_view(), name='ai_question_generator'),
    path('document/', views.DocumentSummarizerView.as_view(), name='ai_document_summarizer'),
]
