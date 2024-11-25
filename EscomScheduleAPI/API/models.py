from django.db import models

class Groups(models.Model):
    group_id = models.AutoField(primary_key=True)
    group_name = models.CharField(max_length=255, unique=True)  # Enforce unique group names

    def __str__(self):
        return self.group_name


class Region(models.Model):
    region_id = models.AutoField(primary_key=True)
    region_name = models.CharField(max_length=255, unique=True)  # Enforce uniqueness

    def __str__(self):
        return self.region_name


class GrpRegion(models.Model):
    group = models.ForeignKey(Groups, on_delete=models.CASCADE)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('group', 'region')  # Ensure each group-region pair is unique

    def __str__(self):
        return f"{self.group.group_name} - {self.region.region_name}"


class Location(models.Model):
    location_id = models.AutoField(primary_key=True)  # Remove unnecessary default
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    location_name = models.CharField(max_length=255)  # Avoid defaults, enforce meaningful input

    def __str__(self):
        return self.location_name


class Areas(models.Model):
    area_id = models.AutoField(primary_key=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    area_name = models.CharField(max_length=255)  # Avoid defaults, enforce meaningful input

    def __str__(self):
        return self.area_name
