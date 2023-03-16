from django.urls import path
from .views import search_aircraft


urlpatterns = [

    path('api/', search_aircraft),
]
