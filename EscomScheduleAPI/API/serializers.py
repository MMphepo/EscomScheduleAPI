from rest_framework import serializers
from .models import Program, Group, Location, Schedule
from datetime import datetime

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['name']

class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = ['date', 'times']

class GroupSerializer(serializers.ModelSerializer):
    locations = LocationSerializer(many=True)
    schedules = ScheduleSerializer(many=True)

    class Meta:
        model = Group
        fields = ['name', 'locations', 'schedules']

class ProgramSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(many=True)

    class Meta:
        model = Program
        fields = ['program_period', 'schedule_date', 'groups']

    def to_internal_value(self, data):
        # Custom date parsing for `schedule_date`
        date_formats = ["%Y-%m-%d", "%d %m %y", "%d-%m-%Y", "%m/%d/%Y","%d/%m/%Y", "%Y/%m/%d", "%Y.%m.%d", "%d.%m.%Y","%B %d, %Y", "%d %B %Y", "%b %d, %Y", "%d %b %Y"     # 12 Nov 2024
]
        schedule_date = data.get("schedule_date")
        
        if schedule_date:
            parsed_date = None
            for fmt in date_formats:
                try:
                    parsed_date = datetime.strptime(schedule_date, fmt).date()
                    break
                except ValueError:
                    continue
            if parsed_date:
                data["schedule_date"] = parsed_date
            else:
                raise serializers.ValidationError({
                    "schedule_date": "Date has wrong format. Use one of these formats: YYYY-MM-DD, DD-MM-YYYY, MM/DD/YYYY."
                })

        return super().to_internal_value(data)
