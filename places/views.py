from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from rest_framework.viewsets import ModelViewSet
from places.serializers import PlaceSerializer
from places.models import Place
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiExample,
)
from drf_spectacular.types import OpenApiTypes
from rest_framework.request import Request


class PlaceViewSet(ModelViewSet):
    queryset = Place.objects.all()
    serializer_class = PlaceSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="geom",
                type=OpenApiTypes.STR,
                required=True,
                description="Coordinates representing the location. "
                            "Should be in the format 'latitude, longitude'. "
                            "For example, '50.44969, 30.522939' represents Kyiv.",
                examples=[
                    OpenApiExample(
                        value="50.44969, 30.522939",
                        name="Kyiv Coordinates",
                    )
                ],
            )
        ],
        description="Create a new place with the given coordinates.",
    )
    def create(self, request: Request, *args, **kwargs) -> Response:
        coordinates = request.data.get("geom").split(", ")
        if coordinates:
            point = Point(
                float(coordinates[0]), float(coordinates[1]), srid=4326
            )
            data = dict(request.data)
            data["geom"] = point

            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
                headers=headers,
            )

        return Response(
            "Invalid coordinates", status=status.HTTP_400_BAD_REQUEST
        )

    def update(self, request: Request, *args, **kwargs) -> Response:
        instance = self.get_object()
        coordinates = request.data.get("geom")
        if coordinates:
            coordinates = coordinates.split(", ")
            if len(coordinates) == 2:
                try:
                    point = Point(
                        float(coordinates[0]), float(coordinates[1]), srid=4326
                    )
                    data = dict(request.data)
                    data["geom"] = point

                    serializer = self.get_serializer(
                        instance, data=data, partial=True
                    )
                    serializer.is_valid(raise_exception=True)
                    self.perform_update(serializer)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                except (TypeError, ValueError):
                    pass
            return Response(
                "Invalid coordinates", status=status.HTTP_400_BAD_REQUEST
            )

        data = dict(request.data)
        serializer = self.get_serializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request: Request, *args, **kwargs) -> Response:
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="lat",
                type=OpenApiTypes.STR,
                required=True,
                description="Latitude of the point to search for the nearest place. Ex for Kyiv: 50.44969",
            ),
            OpenApiParameter(
                name="lon",
                type=OpenApiTypes.STR,
                required=True,
                description="Longitude of the point to search for the nearest place. Ex for Kyiv: 30.522939",
            ),
        ],
        description="Retrieve the nearest place to the specified coordinates.",
    )
    @action(detail=False, methods=["get"], url_path="search-nearest-place")
    def search_nearest_place(self, request: Request) -> Response:
        latitude = request.query_params.get("lat")
        longitude = request.query_params.get("lon")

        if latitude and longitude:
            point = Point(float(latitude), float(longitude), srid=4326)

            nearest_place = (
                Place.objects.annotate(distance=Distance("geom", point))
                .order_by("distance")
                .first()
            )
            serializer = self.get_serializer(nearest_place)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(
            "Latitude and longitude parameters are required",
            status=status.HTTP_400_BAD_REQUEST,
        )
