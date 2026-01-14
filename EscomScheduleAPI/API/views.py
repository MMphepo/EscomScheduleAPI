from django.shortcuts import render
from django.shortcuts import get_object_or_404
import json
# Create your views here.
from psycopg2 import IntegrityError
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Groups, Region, Location, GrpRegion, Areas
from .serializers import GroupsSerializer, LocationSerializer, GrpRegionSerializer, AreasSerializer, RegionSerializer
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
            data = json_data["data"]
        except Exception as e:
            print("DEBUG: Failed to extract 'data' from request.data:", e)
            return Response({"error": "Invalid payload"}, status=status.HTTP_400_BAD_REQUEST)

        print("DEBUG: extracted 'data' keys:", list(data.keys()) if isinstance(data, dict) else None)
        groups = data.get("groups", {})
        print("DEBUG: raw groups count=", len(groups) if isinstance(groups, dict) else 0)
        groups = {oldkey.replace(' ', ''): newkey for oldkey, newkey in groups.items()}
        print("DEBUG: normalized groups keys sample=", list(groups.keys())[:5])
        grpkeys = groups.keys()
        grpids = []
        regiontypes = []
        for key in grpkeys:
            grpid = key[:7]  # 'GROUPA2'
            regiontype = key[8:]
            grpids.append(grpid)
            regiontypes.append(regiontype)
        print("DEBUG: parsed grpids=", grpids)
        print("DEBUG: parsed regiontypes=", regiontypes)

        for name in set(grpids):  # Use `set` to avoid duplicate entries
            group, created = Groups.objects.get_or_create(group_name=name)
            print(f"DEBUG: group {name} ensured (created={created})")

        for name in set(regiontypes):  # Use `set` to avoid duplicate entries
            region, created = Region.objects.get_or_create(region_name=name)
            print(f"DEBUG: region {name} ensured (created={created})")

        affectedAreas = []
        allAreas = []
        locations = []

        # Insert into GrpRegion model
        for grpid, regiontype in zip(grpids, regiontypes):
            print(f"DEBUG: Processing GrpRegion pair: {grpid} - {regiontype}")
            try:
                group = Groups.objects.get(group_name=grpid)
                region = Region.objects.get(region_name=regiontype)

                grp_region, created = GrpRegion.objects.get_or_create(group=group, region=region)
                print(f"DEBUG: GrpRegion {grpid}-{regiontype} (created={created})")

            except Groups.DoesNotExist:
                print(f"DEBUG: Group '{grpid}' does not exist.")
            except Region.DoesNotExist:
                print(f"DEBUG: Region '{regiontype}' does not exist.")
            except IntegrityError as e:
                print(f"DEBUG: Integrity error occurred: {e}")
            except Exception as e:
                print(f"DEBUG: Unexpected error in GrpRegion loop: {e}")

        # Loop through all groups and print affected areas and locations
        for id in groups:
            print(f"DEBUG: Processing group key: {id}")
            affectedArea = groups[id].get("affected_areas", {})
            print("DEBUG: affectedArea keys count=", len(affectedArea) if isinstance(affectedArea, dict) else 0)
            affectedAreas.append(affectedArea)

            print("DEBUG: Collecting locations for this group")
            location = affectedArea.keys()
            locations.append(location)
            print("DEBUG: current locations list sample=", list(location)[:5])

            # handle region-specific insertion
            if id in ["GROUPA1–NORTHERNREGION", "GROUPB1–NORTHERNREGION", "GROUPC1–NORTHERNREGION"]:
                print("DEBUG: northern branch for", id)
                region_name = "NORTHERNREGION"
                try:
                    region = Region.objects.get(region_name=region_name)
                    for singleLocation in location:
                        location_name = singleLocation
                        if not Location.objects.filter(location_name=location_name, region=region).exists():
                            Location.objects.create(location_name=location_name, region=region)
                            print(f"DEBUG: Created Location '{location_name}' under {region_name}")
                        else:
                            print(f"DEBUG: Location '{location_name}' already exists under {region_name}")
                except Region.DoesNotExist:
                    print(f"DEBUG: Region '{region_name}' missing")
                except Exception as e:
                    print(f"DEBUG: Error in northern branch: {e}")

            if id in ("GROUPA1–CENTRALREGION", "GROUPB1–CENTRALREGION", "GROUPB2–CENTRALREGION", "GROUPC1–CENTRALREGION", "GROUPC2–CENTRALREGION"):
                print("DEBUG: central branch for", id)
                region_name = "CENTRALREGION"
                try:
                    region = Region.objects.get(region_name=region_name)
                    for singleLocation in location:
                        location_name = singleLocation
                        if not Location.objects.filter(location_name=location_name, region=region).exists():
                            Location.objects.create(location_name=location_name, region=region)
                            print(f"DEBUG: Created Location '{location_name}' under {region_name}")
                        else:
                            print(f"DEBUG: Location '{location_name}' already exists under {region_name}")
                except Region.DoesNotExist:
                    print(f"DEBUG: Region '{region_name}' missing")
                except Exception as e:
                    print(f"DEBUG: Error in central branch: {e}")

            if id in ("GROUPA1–SOUTHERNREGION", "GROUPA2–SOUTHERNREGION", "GROUPB1–SOUTHERNREGION", "GROUPB2–SOUTHERNREGION", "GROUPC2–SOUTHERNREGION"):
                print("DEBUG: southern branch for", id)
                region_name = "SOUTHERNREGION"
                try:
                    region = Region.objects.get(region_name=region_name)
                    for singleLocation in set(location):
                        location_name = singleLocation
                        if not Location.objects.filter(location_name=location_name, region=region).exists():
                            Location.objects.create(location_name=location_name, region=region)
                            print(f"DEBUG: Created Location '{location_name}' under {region_name}")
                        else:
                            print(f"DEBUG: Location '{location_name}' already exists under {region_name}")
                except Region.DoesNotExist:
                    print(f"DEBUG: Region '{region_name}' missing")
                except Exception as e:
                    print(f"DEBUG: Error in southern branch: {e}")

            print('DEBUG: Processing affected areas for group', id)
            print("DEBUG: present keys =", list(groups[id].get("affected_areas", {}).keys()))
            for single_location in locations:
                print("DEBUG: iterating single_location group entry=", single_location)
                print("DEBUG: affectedArea sample=", dict(list(affectedArea.items())[:3]) if isinstance(affectedArea, dict) else affectedArea)

                from django.db import transaction, connection

                areas = affectedAreas
                try:
                    for entry in areas:
                        for singleLocation in entry:
                            print("DEBUG: Entry location=", singleLocation)
                            if singleLocation not in affectedArea:
                                print(f"DEBUG: No areas defined for location '{singleLocation}'.")
                                continue
                            area_names = affectedArea[singleLocation]
                            print("DEBUG: area_names=", area_names)
                            try:
                                locationss = Location.objects.filter(location_name=singleLocation)
                                if not locationss.exists():
                                    print(f"DEBUG: No locations found with the name '{singleLocation}'.")
                                    continue
                                for location in locationss:
                                    for area_name in area_names:
                                        try:
                                            with transaction.atomic():
                                                if not Areas.objects.filter(area_name=area_name, location=location).exists():
                                                    Areas.objects.create(area_name=area_name, location=location)
                                                    print(f"DEBUG: Created Area '{area_name}' under location '{singleLocation}'")
                                                else:
                                                    print(f"DEBUG: Area '{area_name}' already exists under location '{singleLocation}'")
                                        except Exception as e:
                                            print(f"DEBUG: Error creating area '{area_name}' for '{singleLocation}': {e}")
                            except Exception as e:
                                print(f"DEBUG: Error processing location '{singleLocation}': {e}")
                finally:
                    connection.close()

        groups_qs = Groups.objects.all()
        print("DEBUG: Final groups in DB count=", groups_qs.count())
        for group in groups_qs:
            print("DEBUG: group_name=", group.group_name)

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