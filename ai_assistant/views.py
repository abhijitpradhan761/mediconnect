from django.shortcuts import render
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from accounts.decorators import patient_required
from .forms import SymptomOrganizerForm, QuestionGeneratorForm, DocumentSummarizerForm
from .services import organize_symptoms, generate_doctor_questions, summarize_medical_document


@method_decorator(login_required, name='dispatch')
class AIAssistantHomeView(View):
    """Landing dashboard for the AI Health Preparation tools."""
    def get(self, request):
        return render(request, 'ai_assistant/ai_home.html')


@method_decorator(patient_required, name='dispatch')
class SymptomOrganizerView(View):
    """Interactive symptom structuring tool."""
    def get(self, request):
        form = SymptomOrganizerForm()
        return render(request, 'ai_assistant/symptom_organizer.html', {'form': form})

    def post(self, request):
        form = SymptomOrganizerForm(request.POST)
        result = None
        if form.is_valid():
            result = organize_symptoms(
                symptoms=form.cleaned_data['symptoms'],
                duration=form.cleaned_data['duration'],
                severity=str(form.cleaned_data['severity']),
                context=form.cleaned_data.get('context', '')
            )
        return render(request, 'ai_assistant/symptom_organizer.html', {
            'form': form,
            'result': result,
        })


@method_decorator(patient_required, name='dispatch')
class QuestionGeneratorView(View):
    """Doctor consultation question generator."""
    def get(self, request):
        form = QuestionGeneratorForm()
        return render(request, 'ai_assistant/question_generator.html', {'form': form})

    def post(self, request):
        form = QuestionGeneratorForm(request.POST)
        result = None
        if form.is_valid():
            result = generate_doctor_questions(
                symptoms=form.cleaned_data['symptoms'],
                appointment_reason=form.cleaned_data.get('appointment_reason', '')
            )
        return render(request, 'ai_assistant/question_generator.html', {
            'form': form,
            'result': result,
        })


@method_decorator(patient_required, name='dispatch')
class DocumentSummarizerView(View):
    """Plain-language medical text summarizer."""
    def get(self, request):
        form = DocumentSummarizerForm()
        return render(request, 'ai_assistant/document_summarizer.html', {'form': form})

    def post(self, request):
        form = DocumentSummarizerForm(request.POST)
        result = None
        if form.is_valid():
            result = summarize_medical_document(
                document_text=form.cleaned_data['document_text']
            )
        return render(request, 'ai_assistant/document_summarizer.html', {
            'form': form,
            'result': result,
        })
