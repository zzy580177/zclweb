from django.shortcuts import render, redirect
#Create your views here.
from django.db.models import Q
from appzclamf.models import  *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from appzclamf.api.serializars import *
import datetime

class LiveStatsView(APIView):
    def get(self, request, *args, **kwargs):
        l_cellaID = kwargs.get("cellaId") #request.CellaID
        l_liveStatses = LiveStats.objects.order_by('-id').filter( CellaID=l_cellaID)
        l_liveStatses_json = LiveStatsModelSerializer(l_liveStatses, many=True)
        return Response(l_liveStatses_json.data)

class PezziView(APIView):
    def get(self, request, *args, **kwargs):
        l_cellaID = kwargs.get("cellaId") #request.CellaID
        l_Pezzi = Pezzi.objects.filter( CellaID=l_cellaID)
        l_Pezzi_json = PezziModelSerializer(l_Pezzi, many=True)
        return Response(l_Pezzi_json.data)

class StatoView(APIView):
    def get(self, request, *args, **kwargs):
        l_cellaID = kwargs.get("cellaId") #request.CellaID
        l_Stato = Stato.objects.filter( CellaID=l_cellaID)
        l_Stato_json = PezziModelSerializer(l_Stato, many=True)
        return Response(l_Stato_json.data)

