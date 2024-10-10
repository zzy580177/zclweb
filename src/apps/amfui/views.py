from django.shortcuts import render
from django.db.models import Sum, Q, FloatField,F,Value, FloatField
from django.db.models.functions import Concat, Cast, TruncDate,Trunc, Extract, Coalesce
from .models import *
from datetime import datetime, timedelta, date, time
from django.http import HttpResponse
# Create your views here.
def index(request):
    return render(request, 'amfui/index.html')

def dashboard(request):
    return render(request, 'dashboard.html')

def extend_home(request):
    return render(request, 'extend_home.html')

