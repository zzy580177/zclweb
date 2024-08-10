
from django.urls import path
from appzclamf import views
from appzclamf.api import api_views

urlpatterns = [
    path('index/', views.index),
    path('order/', views.listOrder),
    path("alarm/", views.alarm),
    path("pezzi/", views.pezzi),
    path("stato/", views.stato),
    path("livestats/", views.livestats),
    path("livestats/detal/", views.livestats_detal),
    path("building/", views.building),
    path("api/CellData/<cellaId>", api_views.CellsView.as_view()),
    path("api/Order/<status>", api_views.OrderView.as_view())
    #path("api/livestats/<cellaId>", api_views.LiveStatsView.as_view()),
    #path("api/Stato/<cellaId>", api_views.StatoView.as_view()),
    #path("api/Pezzi/<cellaId>", api_views.PezziView.as_view()),
]

