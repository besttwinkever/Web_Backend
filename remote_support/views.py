from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from remote_support.serializers import AppealSerializer, AppealIssuesSerializer, IssueSerializer, UserSerializer
from remote_support.models import Appeal, AppealIssues, Issue
import remote_support.minio as minio
from datetime import datetime
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password

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
        search = ''
        if 'issue_name' in request.GET:
            search = request.GET['issue_name']
        issues = self.model_class.objects.filter(is_active=True, name__icontains=search).all()
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
        status = None; min_time_applied = None; max_time_applied = None
        if 'status' in request.GET:
            status = int(request.GET['issue_name'])
        if 'min_time_applied' in request.GET:
            min_time_applied = datetime.fromisoformat(request.GET['min_time_applied'])
        if 'max_time_applied' in request.GET:
            max_time_applied = datetime.fromisoformat(request.GET['max_time_applied'])

        appeals = self.model_class.objects.filter(client_id=getActiveUserId()).exclude(status_id__in=[1, 2]).all()

        if status != None:
            appeals = appeals.filter(status_id=status)
        if min_time_applied != None and max_time_applied != None:
            appeals = appeals.filter(time_applied__range=[min_time_applied, max_time_applied])

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

        appeal.time_applied = datetime.now()
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

        appeal.helper_id = getActiveUserId()
        appeal.time_ended = datetime.now()
        appeal.status_id = apply and 5 or 4
        appeal.save()
        serializer = self.serializer(appeal)
        return Response(serializer.data)
    
class AppealRemoveIssue(APIView):
    model_class = AppealIssues
    serializer = AppealIssuesSerializer

    def delete(self, request, appeal_id, issue_id):
        try:
            appeal_issue = AppealIssues.objects.get(appeal_id=appeal_id, issue_id=issue_id)
        except AppealIssues.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        appeal_issue.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class AppealEditIssue(APIView):
    model_class = AppealIssues
    serializer = AppealIssuesSerializer

    def put(self, request, appeal_id, issue_id):
        try:
            appeal_issue = AppealIssues.objects.get(appeal_id=appeal_id, issue_id=issue_id)
        except AppealIssues.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer(appeal_issue, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserDetail(APIView):
    model_class = get_user_model()
    serializer = UserSerializer

    def put(self, request):
        user = get_user_model().objects.get(pk=getActiveUserId())
        return Response(self.serializer(user).data)
    
class UserRegister(APIView):
    model_class = get_user_model()
    serializer = UserSerializer

    def post(self, request):
        if not request.data.get('username') or not request.data.get('password') or not request.data.get('email'):
            return Response({"error": "Не указаны данные для регистрации"}, status=status.HTTP_400_BAD_REQUEST)

        if self.model_class.objects.filter(username=request.data.get('username')).exists() or self.model_class.objects.filter(email=request.data.get('email')).exists():
            return Response({"error": "Пользователь с таким именем/почтой уже существует"}, status=status.HTTP_400_BAD_REQUEST)

        user = self.model_class.objects.create_user(username=request.data.get('username'), password=request.data.get('password'), email=request.data.get('email'))
        return Response(self.serializer(user).data)
    
class UserLogin(APIView):
    model_class = get_user_model()
    serializer = UserSerializer

    def post(self, request):
        if not request.data.get('username') or not request.data.get('password'):
            return Response({"error": "Не указаны данные для авторизации"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = self.model_class.objects.get(username=request.data.get('username'))
        except self.model_class.DoesNotExist:
            return Response({"error": "Неверный логин или пароль"}, status=status.HTTP_400_BAD_REQUEST)
        if not check_password(request.data.get('password'), user.password):
            return Response({"error": "Неверный логин или пароль"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(self.serializer(user).data)
    
class UserLogout(APIView):
    def post(self, request):
        return Response(status=status.HTTP_204_NO_CONTENT)