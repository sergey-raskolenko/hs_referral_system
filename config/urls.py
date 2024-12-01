"""
URL configuration for config project.

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

from user.api_views import LoginAPIView, LogoutAPIView, OTPAPIView, ProfileAPIView
from user.views import  check_otp, login_page, generate_otp, profile_page, enter_invite_code, logout_view


urlpatterns = [
    path('admin/', admin.site.urls),
    path('check/', check_otp, name="check_otp"),
    path('login/', login_page, name="login"),
    path('', logout_view, name="logout"),
    path('otp/<int:pk>/<uuid>/', generate_otp),
    path('<str:invite_code>/', profile_page, name="profile"),
    path('<str:invite_code>/enter_invite_code/', enter_invite_code, name="enter_invite_code"),

    path('api/login/', LoginAPIView.as_view(), name="api-login"),
    path('api/logout/', LogoutAPIView.as_view(), name="api-logout"),
    path('api/<int:pk>/<uuid>/', OTPAPIView.as_view(), name="api-otp-check"),
    path('api/profile/', ProfileAPIView.as_view(), name="api-profile"),

]
