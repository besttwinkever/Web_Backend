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
    
class AppealList(APIView):
    model_class = Appeal
    serializer = AppealSerializer

    def get(self, request):
        appeals = self.model_class.objects.filter(client_id=getActiveUserId()).exclude(status_id__in=[2]).all() #TODO: поставить нормальные id после тестов (добавить 1)
        serializer = self.serializer(appeals, many=True)
        return Response(serializer.data)
    
class AppealDetail(APIView):
    model_class = Appeal
    serializer = AppealSerializer

    def get(self, request, appeal_id):
        try:
            appeal = self.model_class.objects.get(pk=appeal_id, client_id=getActiveUserId())
        except self.model_class.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer(appeal)
        issues = AppealIssues.objects.filter(appeal_id=appeal.id).all()
        issues_serializer = AppealIssuesSerializer(issues, many=True)
        return Response({
            'appeal': serializer.data,
            'issues': issues_serializer.data
        })

    def put(self, request, appeal_id):
        try:
            appeal = self.model_class.objects.get(pk=appeal_id, client_id=getActiveUserId())
        except self.model_class.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer(appeal, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, appeal_id):
        try:
            appeal = self.model_class.objects.get(pk=appeal_id, client_id=getActiveUserId())
        except self.model_class.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        if appeal.status_id != 1:
            return Response({"error": "Некорректное обращение"}, status=status.HTTP_400_BAD_REQUEST)

        appeal.status_id = 2
        appeal.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class AppealConfirm(APIView):
    model_class = Appeal
    serializer = AppealSerializer

    def put(self, request, appeal_id):
        try:
            appeal = self.model_class.objects.get(pk=appeal_id, client_id=getActiveUserId())
        except self.model_class.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        if appeal.status_id != 1:
            return Response({"error": "Некорректное обращение"}, status=status.HTTP_400_BAD_REQUEST)

        if len(appeal.connection_code) == 0:
            return Response({"error": "Код подключения не указан."})

        appeal.status_id = 3
        appeal.save()
        serializer = self.serializer(appeal)
        return Response(serializer.data)
    
class AppealFinish(APIView):
    model_class = Appeal
    serializer = AppealSerializer

    def put(self, request, appeal_id):
        try:
            appeal = self.model_class.objects.get(pk=appeal_id)
        except self.model_class.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        if appeal.status_id != 3:
            return Response({"error": "Некорректное обращение"}, status=status.HTTP_400_BAD_REQUEST)

        apply = request.data.get('apply')
        if apply == None:
            return Response({"error": "Не указано решение по обращению."})

        appeal.status_id = apply and 5 or 4
        appeal.save()
        serializer = self.serializer(appeal)
        return Response(serializer.data)