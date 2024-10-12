"""
URL configuration for drf project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from remote_support import views
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="Snippets API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('issues/', views.IssueList.as_view(), name='issue-list'),
    path('issues/<int:issue_id>/', views.IssueDetail.as_view(), name='issue-detail'),
    path('issues/<int:issue_id>/image', views.IssueImage.as_view(), name='issue-image'),

    path('appeals/', views.AppealList.as_view(), name='appeal-list'),
    path('appeals/<int:appeal_id>/', views.AppealDetail.as_view(), name='appeal-detail'),
    path('appeals/<int:appeal_id>/confirm', views.AppealConfirm.as_view(), name='appeal-confirm'),
    path('appeals/<int:appeal_id>/finish', views.AppealFinish.as_view(), name='appeal-finish'),
    
    path('appeal_issues/<int:issue_id>/', views.AppealIssuesEdit.as_view(), name='appeal-issues'),

    path('user/', views.UserDetail.as_view(), name='user-detail'),
    path('user/register', views.UserRegister.as_view(), name='user-register'),
    path('user/login', views.UserLogin.as_view(), name='user-login'),
    path('user/logout', views.UserLogout.as_view(), name='user-logout'),

    path('admin/', admin.site.urls),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]
