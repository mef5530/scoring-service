# serializers.py
from rest_framework import serializers
from .models import Check, Team, Service, TeamService

class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ['id', 'name', 'score']

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['id', 'name']

class TeamServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamService
        fields = ['id', 'team', 'service', 'uri', 'username', 'password', 'newest_check']

