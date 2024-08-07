from django.http import JsonResponse
from django.shortcuts import render, redirect
#Create your views here.
from django.db.models import Q
from appzclamf.models import  *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from appzclamf.api.serializars import *
from appzclamf.api.dbFilter import *
#from rest_framework_extensions.cache.decorators import cache_response

day = '2024-08-05'
class CellsView(APIView):
    #@cache_response(timeout = 60*1, cache="default")
    def get(self, request, *args, **kwargs):
        l_cellaID = kwargs.get("cellaId") #request.CellaID
        l_cellDatas = getCellaDataForIndex(l_cellaID, day)
        return JsonResponse(l_cellDatas, safe=False, json_dumps_params={'ensure_ascii': False})

class LiveStatsView(APIView):
    #@cache_response(timeout = 60*1, cache="default")
    def get(self, request, *args, **kwargs):
        l_cellaID = kwargs.get("cellaId") #request.CellaID
        l_liveStatses = get_serq_Live(l_cellaID)
        l_liveStatses_json = LiveStatsModelSerializer(l_liveStatses, many=True)
        return Response(l_liveStatses_json.data)

class PezziView(APIView):
    #@cache_response(timeout = 60*1, cache="default")
    def get(self, request, *args, **kwargs):
        l_cellaID = kwargs.get("cellaId") #request.CellaID
        l_Pezzi = get_serq_pezzi(l_cellaID)
        l_Pezzi_json = PezziModelSerializer(l_Pezzi, many=True)
        return Response(l_Pezzi_json.data)

class StatoView(APIView):
    #@cache_response(timeout = 60*1, cache="default")
    def get(self, request, *args, **kwargs):
        l_cellaID = kwargs.get("cellaId") #request.CellaID
        l_Stato = Stato.objects.filter( CellaID=l_cellaID)
        l_Stato_json = PezziModelSerializer(l_Stato, many=True)
        return Response(l_Stato_json.data)

