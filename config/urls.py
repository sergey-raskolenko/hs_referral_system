from django.urls import path

from user.api_views import LoginAPIView, LogoutAPIView, OTPAPIView, ProfileAPIView
from user.views import check_otp, login_page, generate_otp, profile_page, enter_invite_code, logout_view

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="PhoneAuthReferralService",
        default_version='v1',
        description="Авторизация по номеру телефона.",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="sergey.raskolenko@gmail.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('api/login/', LoginAPIView.as_view(), name="api-login"),
    path('api/logout/', LogoutAPIView.as_view(), name="api-logout"),
    path('api/<int:pk>/<str:uuid>/', OTPAPIView.as_view(), name="api-otp-check"),
    path('api/profile/', ProfileAPIView.as_view(), name="api-profile"),
    path('login/', login_page, name="login"),
    path('', logout_view, name="logout"),
    path('otp/<int:pk>/<uuid>/', generate_otp),
    path('check/', check_otp, name="check_otp"),
    path('<str:invite_code>/', profile_page, name="profile"),
    path('<str:invite_code>/enter_invite_code/', enter_invite_code, name="enter_invite_code"),
]
