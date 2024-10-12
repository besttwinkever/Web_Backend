from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.views import APIView
from remote_support.serializers import *
from remote_support.models import Appeal, AppealIssues, Issue
from remote_support.permissions import IsHelper, IsAuthenticated
import remote_support.minio as minio
from datetime import datetime
from django.contrib.auth import authenticate
from drf_yasg.utils import swagger_auto_schema
import uuid
from .redis_util import getUserBySessionId, session_storage

def method_permission_classes(classes):
    def decorator(func):
        def decorated_func(self, *args, **kwargs):
            self.permission_classes = classes        
            self.check_permissions(self.request)
            return func(self, *args, **kwargs)
        return decorated_func
    return decorator

def getActiveAppealForUser(request, addIfNotExists=True):
    appeal = None
    user = getUserBySessionId(request)
    if user == None:
        return None
    try:
        appeal = Appeal.objects.get(client_id=user.pk, status_id=1)
    except Appeal.DoesNotExist:
        if addIfNotExists:
            appeal = Appeal.objects.create(client_id=user.pk, status_id=1)
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
        appeal = getActiveAppealForUser(request, False)
        return Response({
            'active_appeal': {
                'id': appeal.id if appeal != None else None,
                'count': AppealIssues.objects.filter(appeal_id=appeal.id).count() if appeal != None else 0
            },
            'issues': serializer.data
        })
    
    @swagger_auto_schema(request_body=IssueSerializer)
    @method_permission_classes([IsHelper])
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
    
    @swagger_auto_schema(request_body=IssueSerializer)
    @method_permission_classes([IsHelper])
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
    
    @method_permission_classes([IsHelper])
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

    permission_classes = [IsHelper]

    @swagger_auto_schema(request_body=IssueImageSerializer)
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
    
class AppealList(APIView):
    model_class = Appeal
    serializer = AppealSerializer

    permission_classes = [IsAuthenticated]
    def get(self, request):
        status = None; min_time_applied = None; max_time_applied = None
        if 'status' in request.GET:
            status = int(request.GET['status'])
        if 'min_time_applied' in request.GET:
            min_time_applied = datetime.fromisoformat(request.GET['min_time_applied'])
        if 'max_time_applied' in request.GET:
            max_time_applied = datetime.fromisoformat(request.GET['max_time_applied'])

        user = getUserBySessionId(request)

        if user.is_staff or user.is_superuser:
            appeals = self.model_class.objects.filter().exclude(status_id__in=[1, 2]).all()
        else:
            appeals = self.model_class.objects.filter(client_id=user.pk).exclude(status_id__in=[1, 2]).all()

        if status != None:
            appeals = appeals.filter(status_id=status)
        if min_time_applied != None and max_time_applied != None:
            appeals = appeals.filter(time_applied__range=[min_time_applied, max_time_applied])

        for appeal in appeals:
            issues = AppealIssues.objects.filter(appeal_id=appeal.id).all()
            appeal.issues = issues

        serializer = self.serializer(appeals, many=True)
        

        return Response(serializer.data)
    
class AppealDetail(APIView):
    model_class = Appeal
    serializer = AppealSerializer

    permission_classes = [IsAuthenticated]

    def get(self, request, appeal_id):
        user = getUserBySessionId(request)
        try:
            appeal = self.model_class.objects.get(pk=appeal_id, client_id=user.pk)
        except self.model_class.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        issues = AppealIssues.objects.filter(appeal_id=appeal.id).all()
        appeal.issues = issues
        serializer = self.serializer(appeal)
        return Response(serializer.data)
        
    @swagger_auto_schema(request_body=AppealSerializer)
    def put(self, request, appeal_id):
        user = getUserBySessionId(request)
        try:
            appeal = self.model_class.objects.get(pk=appeal_id, client_id=user.pk)
        except self.model_class.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        issues = AppealIssues.objects.filter(appeal_id=appeal.id).all()
        appeal.issues = issues
        serializer = self.serializer(appeal, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, appeal_id):
        user = getUserBySessionId(request)
        try:
            appeal = self.model_class.objects.get(pk=appeal_id, client_id=user.pk)
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

    permission_classes = [IsAuthenticated]

    def put(self, request, appeal_id):
        user = getUserBySessionId(request)
        try:
            appeal = self.model_class.objects.get(pk=appeal_id, client_id=user.pk)
        except self.model_class.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        if appeal.status_id != 1:
            return Response({"error": "Некорректное обращение"}, status=status.HTTP_400_BAD_REQUEST)

        if len(appeal.connection_code) == 0:
            return Response({"error": "Код подключения не указан."}, status=status.HTTP_400_BAD_REQUEST)

        appeal.time_applied = datetime.now()
        appeal.status_id = 3
        appeal.save()
        issues = AppealIssues.objects.filter(appeal_id=appeal.id).all()
        appeal.issues = issues
        serializer = self.serializer(appeal)
        return Response(serializer.data)
    
class AppealFinish(APIView):
    model_class = Appeal
    serializer = AppealSerializer

    permission_classes = [IsHelper]

    @swagger_auto_schema(request_body=AppealSerializer)
    def put(self, request, appeal_id):
        user = getUserBySessionId(request)
        try:
            appeal = self.model_class.objects.get(pk=appeal_id)
        except self.model_class.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        if appeal.status_id != 3:
            return Response({"error": "Некорректное обращение"}, status=status.HTTP_400_BAD_REQUEST)

        apply = request.data.get('apply')
        if apply == None:
            return Response({"error": "Не указано решение по обращению."})

        appeal.helper_id = user.pk
        appeal.time_ended = datetime.now()
        appeal.status_id = apply and 5 or 4
        appeal.average_work_time = 10 * AppealIssues.objects.filter(appeal_id=appeal.id).count()
        appeal.save()
        issues = AppealIssues.objects.filter(appeal_id=appeal.id).all()
        appeal.issues = issues
        serializer = self.serializer(appeal)
        return Response(serializer.data)
    
class AppealIssuesEdit(APIView):
    model_class = AppealIssues
    serializer = AppealIssuesSerializer

    permission_classes = [IsAuthenticated]

    def delete(self, request, issue_id):
        appeal_id = getActiveAppealForUser(request).id
        try:
            appeal_issue = AppealIssues.objects.get(appeal_id=appeal_id, issue_id=issue_id)
        except AppealIssues.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        appeal_issue.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @swagger_auto_schema(request_body=AppealIssuesSerializer)
    def put(self, request, issue_id):
        appeal_id = getActiveAppealForUser(request).id
        try:
            appeal_issue = AppealIssues.objects.get(appeal_id=appeal_id, issue_id=issue_id)
        except AppealIssues.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer(appeal_issue, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def post(self, request, issue_id):
        try:
            issue = Issue.objects.get(pk=issue_id, is_active=True)
        except Issue.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        appeal = getActiveAppealForUser(request)
        AppealIssues.objects.get_or_create(appeal_id=appeal.id, issue_id=issue.id, defaults={'count': 1})

        serializer = self.serializer(AppealIssues.objects.filter(appeal_id=appeal.id).all(), many=True)

        return Response(serializer.data)
    

class UserDetail(APIView):
    model_class = get_user_model()
    serializer = UserSerializer

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=UserSerializer)
    def put(self, request):
        user = getUserBySessionId(request)
        serializer = self.serializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class UserRegister(APIView):
    model_class = get_user_model()
    serializer = UserSerializer

    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(request_body=UserLoginSerializer)
    def post(self, request):
        if not request.data.get('password') or not request.data.get('email'):
            return Response({"status": "Не указаны данные для регистрации"}, status=status.HTTP_400_BAD_REQUEST)

        if self.model_class.objects.filter(email=request.data.get('email')).exists():
            return Response({"status": "Пользователь с такими данными уже существует"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        self.model_class.objects.create_user(
            username=request.data['username'],
            email=request.data['email'], 
            password=request.data['password'],
            is_staff=False,
            is_superuser=False
        )
        return Response({'status': 'Успех'}, status=status.HTTP_200_OK)
    
class UserLogin(APIView):
    model_class = get_user_model()
    serializer = UserSerializer

    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(request_body=UserLoginSerializer)
    def post(self, request):
        if not request.data.get('username') or not request.data.get('password'):
            return Response({"error": "Не указаны данные для авторизации"}, status=status.HTTP_400_BAD_REQUEST)
        
        user = authenticate(username=request.data['username'], password=request.data['password'])
        if user is not None:
            random_key = uuid.uuid4().hex
            for key in session_storage.scan_iter():
                if session_storage.get(key).decode('utf-8') == user.email:
                    session_storage.delete(key)
            session_storage.set(random_key, user.email)
            response = Response(self.serializer(user).data)
            response.set_cookie('session_id', random_key)
            return response
        
        return Response({"error": "Неверный логин или пароль"}, status=status.HTTP_400_BAD_REQUEST)
    
class UserLogout(APIView):
    def post(self, request):
        session_id = request.COOKIES.get('session_id')
        session_storage.delete(session_id)
        return Response(status=status.HTTP_204_NO_CONTENT)