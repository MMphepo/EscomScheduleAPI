from django.urls import path
from .views import  ProgramView, Groupss, Areass, GroupRegionss, Locationss, Regionss, LocationByGroupAndRegion, AreaByGroupRegionLocation

urlpatterns = [
     path('programs/', ProgramView.as_view(), name='program-list'),
     path('groups/', Groupss.as_view(), name='groups'),
     path('regions/', Regionss.as_view(), name='get_regions'),
     path('group-regions/', GroupRegionss.as_view(), name='get_group_regions'),
     path('locations/', Locationss.as_view(), name='get_locations'),
     path('areas/', Areass.as_view(), name='get_areas'),
     path('locations/<str:group_name>/<str:region_name>/', LocationByGroupAndRegion.as_view(), name='location_by_area_and_region'),
     path('areas/<str:group_name>/<str:region_name>/<str:location_name>/', AreaByGroupRegionLocation.as_view(), name='area_by_group_region_location'),
]