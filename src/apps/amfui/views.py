from django.shortcuts import render, redirect
from .models import *
from django.http import HttpResponse
from datetime import datetime, timedelta, time
from django.contrib import messages
from django.db.models import Case, When, Value, IntegerField, Q,F, BooleanField, ExpressionWrapper, DateField


def check_screen_type(request):
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    is_mobile = any(keyword in user_agent for keyword in [
        'Android', 'iPhone', 'iPad', 'iPod', 'BlackBerry', 'Windows Phone'
    ])
    if is_mobile:
        return 1
    else:
        return 3


# Create your views here.
def index(request):
    return render(request, 'amfui/index.html')

def dashboard(request):
    viewsize = check_screen_type(request)
    if request.method=="POST":
        offset = request.POST.get("offset")
    if (viewsize == 3):
        return render(request, 'dashboard.html', {'offset':0,'viewsize':viewsize})
    else:
        return render(request, 'dashboard_min.html', {'offset':0,'viewsize':viewsize})

def extend_home(request):
    offset = 3;
    if request.method=="POST":
        offset = request.POST.get("offset")
    return render(request, 'extend_home.html', {'offset':offset})

# Create your views here.