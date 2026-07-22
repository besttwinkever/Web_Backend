from remote_support.models import Appeal, Issue, AppealIssues
from rest_framework import serializers
from django.contrib.auth import get_user_model

class IssueSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    image = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = Issue
        fields = ['id', 'name', 'description', 'image']

class AppealIssuesSerializer(serializers.ModelSerializer):
    issue = IssueSerializer(read_only=True)
    class Meta:
        model = AppealIssues
        fields = ['issue', 'count']

class AppealSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    client = serializers.StringRelatedField(read_only=True)
    helper = serializers.StringRelatedField(read_only=True)
    status_id = serializers.IntegerField(read_only=True)
    time_created = serializers.DateTimeField(read_only=True)
    time_applied = serializers.DateTimeField(read_only=True)
    time_ended = serializers.DateTimeField(read_only=True)
    issues = serializers.SerializerMethodField()

    class Meta:
        model = Appeal
        fields = ['id', 'client', 'helper', 'status_id', 'time_created', 'time_applied', 'time_ended', 'connection_code', 'average_work_time', 'issues']

    def get_issues(self, obj):
        appeal_issues = AppealIssues.objects.filter(appeal_id=obj.id).select_related('issue')
        return AppealIssuesSerializer(appeal_issues, many=True).data

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
