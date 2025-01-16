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
        json_data = request.data
        data = json_data["data"]
        groups = data["groups"]
        groups = {oldkey.replace(' ', ''): newkey for oldkey, newkey in groups.items()}
        grpkeys=groups.keys()
        grpids = []
        regiontypes = []
        for key in grpkeys:
            grpid = key[:7] # 'GROUPA2' 
            regiontype = key[8:] # 'SOUTHERNREGION' 
            grpids.append(grpid)
            regiontypes.append(regiontype) 
        #print(grpids)
        print(regiontypes)

        for name in set(grpids):  # Use `set` to avoid duplicate entries
            group, created = Groups.objects.get_or_create(group_name=name)
            if created:
                print(f"Inserted: {group.group_name}")
            else:
                print(f"Skipped (already exists): {group.group_name}")
        
        for name in set(regiontypes):  # Use `set` to avoid duplicate entries
            region, created = Region.objects.get_or_create(region_name=name)
            if created:
                print(f"Inserted: {region.region_name}")
            else:
                print(f"Skipped (already exists): {region.region_name}")
        affectedAreas = []
        allAreas = []
        locations = []
          # Insert into GrpRegion model
        for grpid, regiontype in zip(grpids, regiontypes):
            try:
                group = Groups.objects.get(group_name=grpid)
                region = Region.objects.get(region_name=regiontype)
                
                # Check and insert into GrpRegion
                grp_region, created = GrpRegion.objects.get_or_create(group=group, region=region)
                if created:
                    print(f"Inserted GrpRegion: {group.group_name} - {region.region_name}")
                else:
                    print(f"Skipped GrpRegion (already exists): {group.group_name} - {region.region_name}")
            
            except Groups.DoesNotExist:
                print(f"Group '{grpid}' does not exist.")
            except Region.DoesNotExist:
                print(f"Region '{regiontype}' does not exist.")
            except IntegrityError as e:
                print(f"Integrity error occurred: {e}")
            except Exception as e:
                print(f"An error occurred: {e}")
        # Loop through all groups and print affected areas and locations
        for id in groups:
            affectedArea = groups[id]["affected_areas"]
            
            print("the current region = ", id)
            #print("-------------------affected areas-----------")
            #print(affectedAarea)
            affectedAreas.append(affectedArea)
            
            print("------------locations--------------------")
            location = affectedArea.keys()
            locations.append(location)
            print(locations)
            
            if id in ["GROUPA1–NORTHERNREGION", "GROUPB1–NORTHERNREGION", "GROUPC1–NORTHERNREGION"]:
                print("northern")
                region_name = "NORTHERNREGION"
                
                try:
                    # Get the region object (and its id) based on the region_name
                    region = Region.objects.get(region_name=region_name)
                    
                    # Loop through unique locations and check if they exist
                    for singleLocation in location:
                        location_name = singleLocation

                        # Check if the location already exists
                        if not Location.objects.filter(location_name=location_name, region=region).exists():
                            # Create the location if it doesn't exist
                            Location.objects.create(location_name=location_name, region=region)
                            print(f"Location '{location_name}' added successfully under region '{region_name}' (Region ID: {region.region_id}).")
                        else:
                            print(f"Location '{location_name}' already exists under region '{region_name}'.")
                
                except Region.DoesNotExist:
                    print(f"Region with name '{region_name}' does not exist.")
                except Exception as e:
                    print(f"An error occurred: {e}")
            
            if(id == "GROUPA1–CENTRALREGION" or id == "GROUPB1–CENTRALREGION" or id =="GROUPB2–CENTRALREGION" or id == "GROUPC1–CENTRALREGION" or id == "GROUPC2–CENTRALREGION"):
                print("central") 
                region_name = "CENTRALREGION"
                
                try:
                    # Get the region object (and its id) based on the region_name
                    region = Region.objects.get(region_name=region_name)
                    
                    # Loop through unique locations and check if they exist
                    for singleLocation in location:
                        location_name = singleLocation

                        # Check if the location already exists
                        if not Location.objects.filter(location_name=location_name, region=region).exists():
                            # Create the location if it doesn't exist
                            Location.objects.create(location_name=location_name, region=region)
                            print(f"Location '{location_name}' added successfully under region '{region_name}' (Region ID: {region.region_id}).")
                        else:
                            print(f"Location '{location_name}' already exists under region '{region_name}'.")
                
                except Region.DoesNotExist:
                    print(f"Region with name '{region_name}' does not exist.")
                except Exception as e:
                    print(f"An error occurred: {e}")
            
            if(id == "GROUPA1–SOUTHERNREGION" or id == "GROUPA2–SOUTHERNREGION" or id == "GROUPB1–SOUTHERNREGION" or id == "GROUPB2–SOUTHERNREGION" or id == "GROUPC2–SOUTHERNREGION"):
                print("southen")
                region_name = "SOUTHERNREGION"
                
                try:
                    # Get the region object (and its id) based on the region_name
                    region = Region.objects.get(region_name=region_name)
                    
                    # Loop through unique locations and check if they exist
                    for singleLocation in set(location):
                        location_name = singleLocation

                        # Check if the location already exists
                        if not Location.objects.filter(location_name=location_name, region=region).exists():
                            # Create the location if it doesn't exist
                            Location.objects.create(location_name=location_name, region=region)
                            print(f"Location '{location_name}' added successfully under region '{region_name}' (Region ID: {region.region_id}).")
                        else:
                            print(f"Location '{location_name}' already exists under region '{region_name}'.")
                
                except Region.DoesNotExist:
                    print(f"Region with name '{region_name}' does not exist.")
                except Exception as e:
                    print(f"An error occurred: {e}")
            
            print('')
            print("present keys =",groups[id]["affected_areas"].keys())    
            for single_location in locations:
                print
                print("the current location",single_location)
                print(affectedArea)
                
                from django.db import transaction, connection

                # Example areas and their corresponding locations
                areas = affectedAreas

                try:
                    for entry in areas:
                        for singleLocation in entry:
                            print("Entry:", singleLocation)

                            # Ensure the location name exists in the affectedArea dictionary
                            if singleLocation not in affectedArea:
                                print(f"No areas defined for location '{singleLocation}'.")
                                continue

                            # Extract area names
                            area_names = affectedArea[singleLocation]
                            print("Area Names:", area_names)

                            try:
                                # Fetch all matching locations by name
                                locationss = Location.objects.filter(location_name=singleLocation)

                                if not locationss.exists():
                                    print(f"No locations found with the name '{singleLocation}'.")
                                    continue

                                # Loop through all matching locations
                                for location in locationss:
                                    for area_name in area_names:
                                        try:
                                            with transaction.atomic():
                                                # Check if the area already exists for the location
                                                if not Areas.objects.filter(area_name=area_name, location=location).exists():
                                                    Areas.objects.create(area_name=area_name, location=location)
                                                    print(f"Area '{area_name}' added successfully under location '{singleLocation}'.")
                                                else:
                                                    print(f"Area '{area_name}' already exists under location '{singleLocation}'.")
                                        except Exception as e:
                                            print(f"An error occurred while processing area '{area_name}' under location '{singleLocation}': {e}")
                            except Exception as e:
                                print(f"An error occurred while processing location '{singleLocation}': {e}")
                finally:
                    connection.close() # Close the database connection


                 
        groups = Groups.objects.all()
        for group in groups:
            print(group.group_name)
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
