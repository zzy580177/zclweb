from rest_framework import serializers
from appzclamf.models import *

class AlarmModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alarm
        fields ="__all__"

class LiveStatsModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = LiveStats
        fields ="__all__"

class PezziModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pezzi
        fields ="__all__"

class StatoModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stato
        fields ="__all__"