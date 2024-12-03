from django.urls import path
from .views import  ProgramView, Groupss, Areass, GroupRegionss, Locationss, Regionss

urlpatterns = [
     path('programs/', ProgramView.as_view(), name='program-list'),
     path('groups/', Groupss.as_view(), name='groups'),
     path('regions/', Regionss.as_view(), name='get_regions'),
     path('group-regions/', GroupRegionss.as_view(), name='get_group_regions'),
     path('locations/', Locationss.as_view(), name='get_locations'),
     path('areas/', Areass.as_view(), name='get_areas'),
]