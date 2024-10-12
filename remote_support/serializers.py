from remote_support.models import Appeal, Issue, AppealIssues
from rest_framework import serializers
from django.contrib.auth import get_user_model
from collections import OrderedDict

class IssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = ['id', 'name', 'description', 'image']
        read_only_fields = ['id', 'image']


class AppealIssuesSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppealIssues
        fields = ['issue', 'count']
        read_only_fields = ['issue']

class AppealSerializer(serializers.ModelSerializer):
    issues = AppealIssuesSerializer(many=True, read_only=True)
    client = serializers.StringRelatedField()
    helper = serializers.StringRelatedField()

    class Meta:
        model = Appeal
        fields = ['id', 'client', 'helper', 'status_id', 'time_created', 'time_applied', 'time_ended', 'connection_code', 'average_work_time', 'issues']
        read_only_fields = ['id', 'client', 'helper', 'status_id', 'time_created', 'time_applied', 'time_ended', 'average_work_time', 'issues']

class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser']
        read_only_fields = ['username', 'email', 'is_staff', 'is_superuser']

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    class Meta:
        fields = ['username', 'password']

class UserRegisterSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.CharField()
    password = serializers.CharField()

    class Meta:
        fields = ['username', 'email', 'password']

class IssueImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField()
    class Meta:
        model = Issue
        fields = ['image']