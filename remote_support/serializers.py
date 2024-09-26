from remote_support.models import Appeal, Issue, AppealIssues
from rest_framework import serializers

class AppealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appeal
        fields = ['id', 'client_id', 'helper_id', 'status_id', 'time_created', 'time_applied', 'time_ended', 'connection_code']

class IssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = ['id', 'name', 'description', 'image']

class AppealIssuesSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppealIssues
        fields = ['id', 'appeal_id', 'issue_id', 'count']