from django.contrib.gis.db import models


class Place(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    geom = models.PointField()

    class Meta:
        app_label = "places"

    def __str__(self):
        return self.name
