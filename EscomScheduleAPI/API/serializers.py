from rest_framework import serializers
from API.models import Groups, Region, GrpRegion, Location, Areas  # Replace API with your app name

class GroupsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Groups
        fields = ['group_id', 'group_name']  # Include fields you want to expose
class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ['region_id', 'region_name']


class GrpRegionSerializer(serializers.ModelSerializer):
    group = GroupsSerializer()
    region = RegionSerializer()

    class Meta:
        model = GrpRegion
        fields = ['group', 'region']


class LocationSerializer(serializers.ModelSerializer):
    region = RegionSerializer()

    class Meta:
        model = Location
        fields = ['location_id', 'region', 'location_name']

class LocationIDSerializer(serializers.ModelSerializer):
    region = RegionSerializer()

    class Meta:
        model = Location
        fields = ['location_id']
        
class AreasSerializer(serializers.ModelSerializer):
    location = LocationIDSerializer()

    class Meta:
        model = Areas
        fields = ['area_id', 'location', 'area_name']