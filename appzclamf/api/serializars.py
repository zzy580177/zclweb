from rest_framework import serializers
from appzclamf.models import *

class AlarmModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alarmi
        fields ="__all__"

class LiveStatsModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = LiveState
        fields ="__all__"

class PezziModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pezzi
        fields ="__all__"

class StatoModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stato
        fields ="__all__"

class PezziModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pezzi
        fields ="__all__"

class OrderModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields ="__all__"

class OrderRecordModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderHistory
        fields ="__all__"