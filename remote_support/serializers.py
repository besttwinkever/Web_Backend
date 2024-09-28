from remote_support.models import Appeal, Issue, AppealIssues
from rest_framework import serializers
from django.contrib.auth import get_user_model

class AppealSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    client = serializers.StringRelatedField(read_only=True)
    helper = serializers.StringRelatedField(read_only=True)
    status_id = serializers.IntegerField(read_only=True)
    time_created = serializers.DateTimeField(read_only=True)
    time_applied = serializers.DateTimeField(read_only=True)
    time_ended = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Appeal
        fields = ['id', 'client', 'helper', 'status_id', 'time_created', 'time_applied', 'time_ended', 'connection_code', 'average_work_time']

class IssueSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    image = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = Issue
        fields = ['id', 'name', 'description', 'image']

class AppealIssuesSerializer(serializers.ModelSerializer):
    issue_id = serializers.IntegerField()
    class Meta:
        model = AppealIssues
        fields = ['issue_id', 'count']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['id', 'username', 'email', 'first_name', 'last_name']