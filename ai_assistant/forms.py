from django import forms


class SymptomOrganizerForm(forms.Form):
    """Form for structuring patient symptoms before a doctor consultation."""
    symptoms = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'e.g. Throbbing headache on the right side, accompanied by mild sensitivity to bright light...'
        }),
        label="What symptoms are you experiencing?",
        help_text="Describe in your own words what you feel."
    )
    duration = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g. 3 days, 2 weeks, intermittently for a month'
        }),
        label="How long have symptoms lasted?"
    )
    severity = forms.IntegerField(
        min_value=1,
        max_value=10,
        initial=5,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': 1,
            'max': 10
        }),
        label="Severity Level (Scale of 1 - 10)",
        help_text="1 = very mild, 10 = extreme/unbearable."
    )
    context = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'e.g. Worse in the morning or after screen work; improved after resting in a dark room...'
        }),
        label="Additional context, triggers, or existing conditions (Optional)"
    )


class QuestionGeneratorForm(forms.Form):
    """Form to generate empowered questions for the patient's visit."""
    symptoms = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'e.g. Persistent lower back discomfort when standing, knee stiffness in cold weather...'
        }),
        label="Health concerns or symptoms to discuss"
    )
    appointment_reason = forms.CharField(
        required=False,
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g. Orthopedic consultation, annual physical, follow-up visit'
        }),
        label="Type of consultation or specialist (Optional)"
    )


class DocumentSummarizerForm(forms.Form):
    """Form for plain language summarization of medical text."""
    document_text = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 6,
            'placeholder': 'Paste the text from your lab report, discharge summary, or radiology note here...'
        }),
        label="Medical Report Text",
        help_text="Paste text from your diagnostic lab report or medical summary."
    )
