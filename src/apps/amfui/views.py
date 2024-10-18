from django.shortcuts import render
from .models import *


# Create your views here.
def index(request):
    return render(request, 'amfui/index.html')

def dashboard(request):
    offset = 4;
    if request.method=="POST":
        offset = request.POST.get("offset")
    return render(request, 'dashboard.html', {'offset':offset})

def extend_home(request):
    offset = 3;
    if request.method=="POST":
        offset = request.POST.get("offset")
    return render(request, 'extend_home.html', {'offset':offset})

def test(request):
    offset = 3;
    if request.method=="POST":
        offset = request.POST.get("offset")
    return render(request, 'test.html', {'offset':offset})

