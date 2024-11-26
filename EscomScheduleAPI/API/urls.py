from django.urls import path
from .views import  ProgramView, GetGroups, GetAreas, GetGroupRegions, GetLocations, GetRegions

urlpatterns = [
     path('programs/', ProgramView.as_view(), name='program-list'),
     path('groups/', GetGroups.as_view(), name='groups'),
     path('regions/', GetRegions.as_view(), name='get_regions'),
     path('group-regions/', GetGroupRegions.as_view(), name='get_group_regions'),
     path('locations/', GetLocations.as_view(), name='get_locations'),
     path('areas/', GetAreas.as_view(), name='get_areas'),
]