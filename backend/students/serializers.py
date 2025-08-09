from rest_framework import serializers
from .models import Results


class ResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Results
        fields = '__all__'