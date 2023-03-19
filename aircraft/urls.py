from django.urls import path
from .views import AircraftList


urlpatterns = [

    path('api/', AircraftList.as_view()),
    # path('api/company/', aircraft_detail),
]
