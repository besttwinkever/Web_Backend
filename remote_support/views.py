from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from remote_support.serializers import AppealSerializer, AppealIssuesSerializer, IssueSerializer
from remote_support.models import Appeal, AppealIssues, Issue
import remote_support.minio as minio

def getActiveUserId():
    return 1

def getActiveAppealForUser(userId):
    appeal = None
    try:
        appeal = Appeal.objects.get(client_id=userId, status_id=1)
    except Appeal.DoesNotExist:
        appeal = Appeal.objects.create(client_id=userId, status_id=1)
    return appeal

class IssueList(APIView):
    model_class = Issue
    serializer = IssueSerializer

    def get(self, request):
        issues = self.model_class.objects.filter(is_active=True).all()
        serializer = self.serializer(issues, many=True)
        return Response({
            'active_appeal_id': getActiveAppealForUser(getActiveUserId()).id,
            'issues': serializer.data
        })
    
    def post(self, request):
        serializer = self.serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class IssueDetail(APIView):
    model_class = Issue
    serializer = IssueSerializer

    def get(self, request, issue_id):
        try:
            issue = self.model_class.objects.get(pk=issue_id, is_active=True)
        except self.model_class.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer(issue)
        return Response(serializer.data)
    
    def put(self, request, issue_id):
        try:
            issue = self.model_class.objects.get(pk=issue_id, is_active=True)
        except self.model_class.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer(issue, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, issue_id):
        try:
            issue = self.model_class.objects.get(pk=issue_id, is_active=True)
        except self.model_class.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        image_result = minio.delete_pic(issue)
        if 'error' in image_result.data:
            return image_result
        issue.is_active = False
        issue.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class IssueImage(APIView):
    model_class = Issue
    serializer = IssueSerializer

    def post(self, request, issue_id):
        try:
            issue = self.model_class.objects.get(pk=issue_id, is_active=True)
        except self.model_class.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer(issue)
        image = request.FILES.get('image')
        image_result = minio.add_pic(issue, image)
        if 'error' in image_result.data:
            return image_result
        return Response(serializer.data)
    
class IssueAdd(APIView):
    model_class = AppealIssues
    serializer = AppealIssuesSerializer

    def post(self, request, issue_id):
        try:
            issue = Issue.objects.get(pk=issue_id, is_active=True)
        except Issue.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        appeal = getActiveAppealForUser(getActiveUserId())
        AppealIssues.objects.get_or_create(appeal_id=appeal.id, issue_id=issue.id, defaults={'count': 1})
        return Response(status=status.HTTP_201_CREATED)