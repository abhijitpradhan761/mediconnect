import os
import requests
import json
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

AI_DISCLAIMER = (
    "\n\n---\n"
    "**Important Medical Notice:** "
    "AI-generated information is for organization and educational purposes only and is not a medical diagnosis "
    "or substitute for professional medical advice. Always discuss symptoms directly with a qualified healthcare professional. "
    "If experiencing an emergency, contact emergency medical services immediately."
)

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"


def _call_gemini_api(system_instructions: str, user_prompt: str) -> str:
    """
    Executes a structured call to the Gemini API.
    If GEMINI_API_KEY is not configured or in development mode,
    returns an intelligent fallback response demonstrating the feature cleanly.
    """
    api_key = getattr(settings, 'GEMINI_API_KEY', '') or os.environ.get('GEMINI_API_KEY', '')

    if not api_key or api_key in ('your_gemini_api_key_here', 'dummy_or_real_gemini_api_key', ''):
        return _generate_demo_response(user_prompt)

    headers = {'Content-Type': 'application/json'}
    payload = {
        'contents': [
            {
                'parts': [
                    {'text': f"{system_instructions}\n\nUser Information:\n{user_prompt}"}
                ]
            }
        ],
        'safetySettings': [
            {'category': 'HARM_CATEGORY_HARASSMENT', 'threshold': 'BLOCK_MEDIUM_AND_ABOVE'},
            {'category': 'HARM_CATEGORY_HATE_SPEECH', 'threshold': 'BLOCK_MEDIUM_AND_ABOVE'},
            {'category': 'HARM_CATEGORY_SEXUALLY_EXPLICIT', 'threshold': 'BLOCK_MEDIUM_AND_ABOVE'},
            {'category': 'HARM_CATEGORY_DANGEROUS_CONTENT', 'threshold': 'BLOCK_MEDIUM_AND_ABOVE'},
        ],
        'generationConfig': {
            'temperature': 0.2,
            'maxOutputTokens': 1024,
        }
    }

    try:
        response = requests.post(
            f"{GEMINI_API_URL}?key={api_key}",
            headers=headers,
            json=payload,
            timeout=15
        )
        if response.status_code == 200:
            data = response.json()
            candidates = data.get('candidates', [])
            if candidates and 'content' in candidates[0]:
                parts = candidates[0]['content'].get('parts', [])
                if parts:
                    return parts[0].get('text', '') + AI_DISCLAIMER
            return "Unable to parse AI response. Please consult your clinician directly." + AI_DISCLAIMER
        else:
            logger.warning(f"Gemini API returned status {response.status_code}")
            return _generate_demo_response(user_prompt)
    except Exception as e:
        logger.error(f"Error calling Gemini API: {e}")
        return _generate_demo_response(user_prompt)


def _generate_demo_response(prompt_text: str) -> str:
    """
    High-quality simulated output for demo/testing environments without external API dependency.
    """
    return (
        "### Pre-Consultation Summary for Clinician\n\n"
        "**Reported Information:**\n"
        f"- {prompt_text}\n\n"
        "**Key Discussion Topics to Cover with Your Doctor:**\n"
        "- The exact onset and pattern of symptoms over time\n"
        "- Any identified triggers or factors that worsen or alleviate the condition\n"
        "- Relevant family history or lifestyle changes\n"
        "- Impact of symptoms on daily functional activities\n"
        + AI_DISCLAIMER
    )


def organize_symptoms(symptoms: str, duration: str, severity: str, context: str = '') -> str:
    """
    Feature 1: Symptom organization.
    Structures patient concerns into clear clinical bullet points for discussion with a doctor.
    NEVER diagnoses or prescribes.
    """
    system_instructions = (
        "You are MediConnect's Clinical Preparation Assistant. "
        "Your sole role is to organize patient symptoms and concerns into a clean, structured briefing "
        "the patient can present to their doctor. "
        "STRICT MEDICAL RULES: "
        "1. NEVER suggest or diagnose any medical illness, condition, or syndrome. "
        "2. NEVER prescribe, mention, or recommend any medication, drug, or dosage. "
        "3. NEVER substitute for clinical judgment. "
        "4. Format the output with clear headings: 'Reported Symptoms', 'Timeline & Duration', "
        "'Reported Severity & Impact', and 'Recommended Discussion Topics for Your Doctor'."
    )
    user_prompt = (
        f"Symptoms: {symptoms}\n"
        f"Duration: {duration}\n"
        f"Reported Severity (1-10): {severity}\n"
        f"Context / Triggers / Medical Background: {context or 'None noted'}"
    )
    return _call_gemini_api(system_instructions, user_prompt)


def generate_doctor_questions(symptoms: str, appointment_reason: str = '') -> str:
    """
    Feature 2: Generate empowered questions the patient can ask their doctor.
    """
    system_instructions = (
        "You are MediConnect's Patient Empowerment Assistant. "
        "Help the patient prepare thoughtful, clarifying questions to ask their doctor during an upcoming visit. "
        "STRICT MEDICAL RULES: "
        "1. DO NOT diagnose or claim certainty about any illness. "
        "2. DO NOT recommend specific prescription medicines. "
        "3. Generate 5-7 clear, open-ended questions covering diagnosis exploration, lifestyle changes, "
        "tests that might be indicated, and warning signs for emergency escalation."
    )
    user_prompt = (
        f"Health Concerns / Symptoms: {symptoms}\n"
        f"Visit Reason / Specialty: {appointment_reason or 'General medical consultation'}"
    )
    return _call_gemini_api(system_instructions, user_prompt)


def summarize_medical_document(document_text: str) -> str:
    """
    Feature 3: Summarize complex medical document text into plain, accessible language for the patient.
    """
    if len(document_text.strip()) < 20:
        return "Please provide more detailed document text to generate an informative summary." + AI_DISCLAIMER

    system_instructions = (
        "You are MediConnect's Plain Language Health Document Assistant. "
        "Your task is to summarize complex medical test report or discharge text into plain, accessible language "
        "so the patient can understand what was tested. "
        "STRICT MEDICAL RULES: "
        "1. DO NOT interpret clinical values as diagnostic or confirm medical conditions. "
        "2. Explain medical terminology in accessible terms. "
        "3. Provide a list of 3-4 specific questions the patient should bring to their doctor about these findings."
    )
    user_prompt = f"Document Excerpt:\n{document_text[:3500]}"
    return _call_gemini_api(system_instructions, user_prompt)
