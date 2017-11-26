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
from django.urls import reverse_lazy

from .views import ActivateView, NewUserView


urlpatterns = [
    url(r'^activate/(?P<user_id>[\d-]+)-(?P<token>[\w-]+)/$', ActivateView.as_view(), name="activate"),
]

from django.contrib.auth import views as auth_views

urlpatterns += [
    url(r'^login/$', auth_views.LoginView.as_view(template_name='accounts/login_template.html',
                    success_url=reverse_lazy('simpleblog:home'),
                    redirect_authenticated_user=False), name="login"),
    url(r'^logout/$', auth_views.LogoutView.as_view(template_name='simpleblog/post_list.html',
                    next_page=reverse_lazy('simpleblog:home')), name="logout"),
    url(r'^signup/$', NewUserView.as_view(), name="signup"),
]
