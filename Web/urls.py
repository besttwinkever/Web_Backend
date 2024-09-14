"""
URL configuration for Web project.

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
from Web import views
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('', views.indexController, name='index'),
    path('issue/<int:id>/', views.issueController, name='issue'),
    path('issue/add/<int:id>/', views.issueAddController, name='issue_add'),
    path('appeal/<int:appealId>/', views.appealController, name='appeal'),
    path('appeal/delete/', views.appealDeleteController, name='appeal_delete'),
    path('admin/', admin.site.urls)
]
