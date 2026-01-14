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


class Schedule(models.Model):
    """Represents a schedule batch (e.g. a program period / date) for a group/region."""
    schedule_id = models.AutoField(primary_key=True)
    group = models.ForeignKey(Groups, on_delete=models.CASCADE, null=True, blank=True)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, null=True, blank=True)
    program_period = models.CharField(max_length=512, blank=True, null=True)
    schedule_date = models.CharField(max_length=64, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        parts = []
        if self.group:
            parts.append(self.group.group_name)
        if self.region:
            parts.append(self.region.region_name)
        return " | ".join(parts) or f"Schedule {self.schedule_id}"


class TimeSlot(models.Model):
    """A time slot entry associated with a Schedule and optionally a Location."""
    timeslot_id = models.AutoField(primary_key=True)
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='timeslots')
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True, blank=True)
    time_text = models.CharField(max_length=128)  # e.g. "08h00 - 12h00"
    ordering = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['ordering', 'timeslot_id']

    def __str__(self):
        loc = self.location.location_name if self.location else "(group)"
        return f"{loc}: {self.time_text}"
