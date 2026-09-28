from rest_framework import serializers


class SymptomOrganizerSerializer(serializers.Serializer):
    symptoms = serializers.CharField(max_length=2000)
    duration = serializers.CharField(max_length=100)
    severity = serializers.IntegerField(min_value=1, max_value=10, default=5)
    context = serializers.CharField(max_length=2000, required=False, allow_blank=True)


class QuestionGeneratorSerializer(serializers.Serializer):
    symptoms = serializers.CharField(max_length=2000)
    appointment_reason = serializers.CharField(max_length=200, required=False, allow_blank=True)


class DocumentSummarizerSerializer(serializers.Serializer):
    document_text = serializers.CharField(max_length=10000)
