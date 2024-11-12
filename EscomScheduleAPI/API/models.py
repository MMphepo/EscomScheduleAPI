from django.db import models
from django.contrib.postgres.fields import ArrayField

class Program(models.Model):
    program_period = models.CharField(max_length=10000, null=True, blank=True)
    schedule_date = models.DateField(null=True, blank=True)

class Group(models.Model):
    program = models.ForeignKey(Program, related_name='groups', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

class Location(models.Model):
    group = models.ForeignKey(Group, related_name='locations', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

class Schedule(models.Model):
    group = models.ForeignKey(Group, related_name='schedules', on_delete=models.CASCADE)
    date = models.DateField()
    times = ArrayField(models.TimeField())
