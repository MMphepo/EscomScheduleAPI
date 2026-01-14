from django.shortcuts import render
from django.shortcuts import get_object_or_404
import json
import re
# Create your views here.
from psycopg2 import IntegrityError
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Groups, Region, Location, GrpRegion, Areas, Schedule, TimeSlot
from .serializers import GroupsSerializer, LocationSerializer, GrpRegionSerializer, AreasSerializer, RegionSerializer, ScheduleSerializer, TimeSlotSerializer
from rest_framework import status
from django.db import transaction, connection

# def InsertAffectedAreas(location):

#     # Example areas and their corresponding locations
#     try:
#         for location_name, area_names in areas.items():
#             try:
#                 # Fetch the location object
#                 location = Location.objects.get(location_name=location_name)
                
#                 for area_name in area_names:
#                     try:
#                         with transaction.atomic():
#                             # Check if the area already exists for the location
#                             if not Areas.objects.filter(area_name=area_name, location=location).exists():
#                                 Areas.objects.create(area_name=area_name, location=location)
#                                 print(f"Area '{area_name}' added successfully under location '{location_name}'.")
#                             else:
#                                 print(f"Area '{area_name}' already exists under location '{location_name}'.")
#                     except Exception as e:
#                         print(f"An error occurred while processing area '{area_name}' under location '{location_name}': {e}")
#             except Location.DoesNotExist:
#                 print(f"Location '{location_name}' does not exist.")
#     finally:
#         connection.close()  # Close the database connection

    
class ProgramView(APIView):
    def post(self, request):
        print("DEBUG: Entered ProgramView.post")
        json_data = request.data
        print("DEBUG: request.data type=", type(json_data))
        try:
            data = json_data.get("data", {})
        except Exception as e:
            print("DEBUG: Failed to extract 'data' from request.data:", e)
            return Response({"error": "Invalid payload"}, status=status.HTTP_400_BAD_REQUEST)

        groups = data.get("groups", {}) if isinstance(data, dict) else {}
        print("DEBUG: groups keys=", list(groups.keys())[:10])

        # flexible separator: en-dash, em-dash or hyphen
        sep_re = re.compile(r"\s*[–—-]\s*")

        created_groups = 0
        created_regions = 0

        for raw_key, group_obj in groups.items():
            print(f"DEBUG: raw group key='{raw_key}'")
            try:
                parts = sep_re.split(raw_key)
                left = parts[0].strip().upper() if parts else raw_key.strip().upper()
                right = parts[1].strip().upper() if len(parts) > 1 else ""

                group_name_norm = left.replace(' ', '')
                region_name_norm = right.replace(' ', '') if right else ""

                group, g_created = Groups.objects.get_or_create(group_name=group_name_norm)
                if g_created:
                    created_groups += 1
                    print(f"DEBUG: Created group '{group_name_norm}'")

                if region_name_norm:
                    region, r_created = Region.objects.get_or_create(region_name=region_name_norm)
                    if r_created:
                        created_regions += 1
                        print(f"DEBUG: Created region '{region_name_norm}'")
                    GrpRegion.objects.get_or_create(group=group, region=region)

                # Insert / ensure locations
                locations_list = group_obj.get('locations', []) if isinstance(group_obj, dict) else []
                for loc_name in locations_list:
                    try:
                        if region_name_norm:
                            region_obj = Region.objects.get(region_name=region_name_norm)
                            if not Location.objects.filter(location_name=loc_name, region=region_obj).exists():
                                Location.objects.create(location_name=loc_name, region=region_obj)
                                print(f"DEBUG: Created Location '{loc_name}' under region '{region_name_norm}'")
                            else:
                                print(f"DEBUG: Location '{loc_name}' already exists under region '{region_name_norm}'")
                        else:
                            if not Location.objects.filter(location_name=loc_name).exists():
                                Location.objects.create(location_name=loc_name)
                                print(f"DEBUG: Created Location '{loc_name}' (no region)")
                            else:
                                print(f"DEBUG: Location '{loc_name}' already exists (no region)")
                    except Exception as e:
                        print(f"DEBUG: Error creating location '{loc_name}': {e}")

                # Insert affected areas
                affected = group_obj.get('affected_areas', {}) if isinstance(group_obj, dict) else {}
                for loc_name, area_names in affected.items():
                    try:
                        locations_qs = Location.objects.filter(location_name=loc_name)
                        if not locations_qs.exists():
                            print(f"DEBUG: No location found for '{loc_name}' when adding areas")
                            continue
                        for location in locations_qs:
                            for area_name in area_names:
                                try:
                                    with transaction.atomic():
                                        if not Areas.objects.filter(area_name=area_name, location=location).exists():
                                            Areas.objects.create(area_name=area_name, location=location)
                                            print(f"DEBUG: Created Area '{area_name}' under location '{loc_name}'")
                                        else:
                                            print(f"DEBUG: Area '{area_name}' already exists under location '{loc_name}'")
                                except Exception as e:
                                    print(f"DEBUG: Error creating area '{area_name}' for '{loc_name}': {e}")
                    except Exception as e:
                        print(f"DEBUG: Affected areas processing error for loc '{loc_name}': {e}")

                # Schedule / times are logged (no model provided)
                times = group_obj.get('times', []) if isinstance(group_obj, dict) else []
                schedule = group_obj.get('schedule', {}) if isinstance(group_obj, dict) else {}
                if times:
                    print(f"DEBUG: Found times for group '{raw_key}': {times}")
                if schedule:
                    print(f"DEBUG: Found schedule mapping for group '{raw_key}': keys={list(schedule.keys())}")

            except Exception as e:
                print(f"DEBUG: Error processing group '{raw_key}': {e}")

        groups_qs = Groups.objects.all()
        print("DEBUG: Final groups in DB count=", groups_qs.count())
        print("DEBUG: Exiting ProgramView.post with success")
        return Response({"status": "success", "groups_count": groups_qs.count()}, status=status.HTTP_201_CREATED)
        # data_cleaning = Datacleaning()
        # data_cleaning.clean_spaces(groups)
        
        
        # serializer = ProgramSerializer(data=request.data.get("data"))
        # if serializer.is_valid():
        #     serializer.save()
        #     return Response(serializer.data, status=status.HTTP_201_CREATED)
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Groupss(APIView):
    def get(self, request):
        groups = Groups.objects.all()
        serializer = GroupsSerializer(groups, many=True)  # Serialize queryset
        return Response(serializer.data, status=status.HTTP_200_OK)

class Areass(APIView):
    def get(self, request):
        areas = Areas.objects.all()
        serializer = AreasSerializer(areas, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class Regionss(APIView):
    def get(self, request):
        regions = Region.objects.all()
        serializer = RegionSerializer(regions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class GroupRegionss(APIView):
    def get(self, request):
        group_regions = GrpRegion.objects.all()
        serializer = GrpRegionSerializer(group_regions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class Locationss(APIView):
    def get(self, request):
        locations = Location.objects.all()
        serializer = LocationSerializer(locations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    


class LocationByGroupAndRegion(APIView):
    def get(self, request, group_name, region_name):
        # Fetch the group and region from the database
        group = get_object_or_404(Groups, group_name=group_name)
        region = get_object_or_404(Region, region_name=region_name)
        
        print("Group:", group)
        print("Region:", region)

        # Retrieve the IDs for the group and region
        group_id = group.group_id  # Assuming 'group_id' is the primary key in Groups
        region_id = region.region_id  # Assuming 'region_id' is the primary key in Region
        print ("group_id", group_id, "region_id", region_id)

        # Check if a GrpRegion entry exists for this group-region pair
        try:
            grp_region = GrpRegion.objects.get(group_id=group_id, region_id=region_id)
            print("GrpRegion:", grp_region)
        except GrpRegion.DoesNotExist:
            return Response(
                {"error": "The group-region combination does not exist."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Retrieve the locations associated with this region
        locations = Location.objects.filter(region=region)
        if not locations.exists():
            return Response(
                {"message": "No locations found for the provided group and region."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Serialize and return the locations
        serializer = LocationSerializer(locations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class AreaByGroupRegionLocation(APIView):
    def get(self, request, group_name, region_name, location_name):
        try:
            # First verify if the group-region combination exists
            group = Groups.objects.get(group_name=group_name)
            region = Region.objects.get(region_name=region_name)
            grp_region = GrpRegion.objects.filter(
                group=group,
                region=region
            ).first()
            
            if not grp_region:
                return Response(
                    {"error": "Invalid group and region combination"},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Get the location
            location = Location.objects.filter(
                region=region,
                location_name=location_name
            ).first()
            
            if not location:
                return Response(
                    {"error": "Location not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Get areas for this location
            areas = Areas.objects.filter(location=location)
            serializer = AreasSerializer(areas, many=True)
            
            return Response(serializer.data)

        except Groups.DoesNotExist:
            return Response(
                {"error": "Group not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Region.DoesNotExist:
            return Response(
                {"error": "Region not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )