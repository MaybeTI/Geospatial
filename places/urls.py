from django.urls import path, include
from rest_framework import routers
from places.views import PlaceViewSet

router = routers.DefaultRouter()
router.register("places", PlaceViewSet, basename="place")

urlpatterns = [
    path("", include(router.urls)),
]

app_name = "places"
