from django.urls import path
from .views import  ProgramView, Groups, Areas, GroupRegions, Locations, Regions

urlpatterns = [
     path('programs/', ProgramView.as_view(), name='program-list'),
     path('groups/', Groups.as_view(), name='groups'),
     path('regions/', Regions.as_view(), name='get_regions'),
     path('group-regions/', GroupRegions.as_view(), name='get_group_regions'),
     path('locations/', Locations.as_view(), name='get_locations'),
     path('areas/', Areas.as_view(), name='get_areas'),
]