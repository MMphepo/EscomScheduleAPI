from django.shortcuts import render
import json
# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response

from rest_framework import status
from .models import Program
from .serializers import ProgramSerializer

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
        print(grpids)
        
        affectedAreas = []
        allAreas = []
        locations = []
        # Loop through all groups and print affected areas and locations
        for id in groups:
            affectedAarea = groups[id]["affected_areas"]
            print("-------------------affected areas-----------")
            print(affectedAarea)
            affectedAreas.append(affectedAarea)
            
            print("------------locations--------------------")
            location = affectedAarea.keys()
            locations.append(location)
            print(location)
            
            for lockey in location:
                areas = affectedAarea[lockey]
                allAreas.extend(areas)
                print("all areas of location--", areas)
        
        
        print("absolutely all areas--",allAreas)

            
        # data_cleaning = Datacleaning()
        # data_cleaning.clean_spaces(groups)
        
        
        # serializer = ProgramSerializer(data=request.data.get("data"))
        # if serializer.is_valid():
        #     serializer.save()
        #     return Response(serializer.data, status=status.HTTP_201_CREATED)
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        programs = Program.objects.all()
        serializer = ProgramSerializer(programs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)