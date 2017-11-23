"""cfe URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin

from .views import (PostCreateView, PostDetailView, PostListView,
                    PostUpdateView, PostLikesToggleView)
from .views import PostsByDateView
#from django.views.generic import TemplateView

urlpatterns = [
    url(r'^create/$', PostCreateView.as_view(), name = 'create-post'),
    url(r'^(?P<pk>[\d]+)/$', PostDetailView.as_view(), name = 'view-post'),
    url(r'^(?P<pk>[\d]+)/like/$', PostLikesToggleView.as_view(), name = 'like-post'),
    url(r'^(?P<pk>[\d]+)/edit/$', PostUpdateView.as_view(), name = 'update-post'),
    url(r'^calendar/(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})/$', PostsByDateView.as_view(), name='calendar'),
    url(r'^tag/(?P<tag>[\w\s-]+)/$', PostListView.as_view(), name = 'tag-posts'),
    url(r'^user/(?P<user>[\w-]+)/$', PostListView.as_view(), name = 'user-posts'),
    url(r'^user/(?P<user>[\w-]+)/drafts/$', PostListView.as_view(), {'drafts': True}, name = 'drafts'),
#    url(r'^activate/(?P<user_id>[\d-]+)-(?P<token>[\w-]+)/$', ActivateView.as_view(), name="activate"),
    url(r'^$', PostListView.as_view(), name = 'home'),
]
