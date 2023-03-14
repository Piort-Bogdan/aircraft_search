from django.urls import path
from .views import search_aircraft


urlpatterns = [

    path('search/', search_aircraft),
]
