from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from places.models import Place
from places.serializers import PlaceSerializer
from django.contrib.gis.geos import Point

PLACE_URL = 'places:place-list'
PLACE_DETAIL_URL = 'places:place-detail'
PLACE_NEAREST_URL = 'places:place-search-nearest-place'


class PlaceViewSetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_create_place(self):
        url = reverse(PLACE_URL)
        data = {
            'name': 'Test Place',
            "description": "description",
            'geom': '12.34, 56.78'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Place.objects.count(), 1)
        place = Place.objects.first()
        self.assertEqual(place.name, 'Test Place')
        self.assertEqual(place.geom, "SRID=4326;POINT (12.34 56.78)")

    def test_update_place(self):
        place = Place.objects.create(name='Test Place', geom=Point(12.34, 56.78))
        url = reverse(PLACE_DETAIL_URL, args=[place.pk])
        data = {
            'name': 'Updated Place',
            'geom': '87.65, 43.21'
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        place.refresh_from_db()
        self.assertEqual(place.name, 'Updated Place')
        self.assertEqual(place.geom, "SRID=4326;POINT (87.65 43.21)")

    def test_partial_update_place(self):
        place = Place.objects.create(name='Test Place', geom=Point(12.34, 56.78))
        url = reverse(PLACE_DETAIL_URL, args=[place.pk])
        data = {
            'geom': '87.65, 43.21'
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        place.refresh_from_db()
        self.assertEqual(place.geom, "SRID=4326;POINT (87.65 43.21)")

    def test_search_nearest_place(self):
        place1 = Place.objects.create(name='Place 1', geom=Point(10, 20))
        place2 = Place.objects.create(name='Place 2', geom=Point(30, 40))
        place3 = Place.objects.create(name='Place 3', geom=Point(50, 60))

        url = reverse(PLACE_NEAREST_URL)
        response = self.client.get(url, {'lat': '35', 'lon': '45'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serializer = PlaceSerializer(place2)
        self.assertEqual(response.data, serializer.data)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
