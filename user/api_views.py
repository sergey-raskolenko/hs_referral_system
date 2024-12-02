from time import sleep

from django.contrib.auth import authenticate, login, logout

from phonenumber_field.validators import validate_international_phonenumber
from rest_framework import status
from rest_framework.generics import CreateAPIView, ListAPIView, ListCreateAPIView
from rest_framework.response import Response

from user.api_serializers import UserSerializer
from user.forms import LoginForm
from user.models import User
from user.services import OTP
import uuid


class LoginAPIView(CreateAPIView):
    """Контроллер для авторизации и генерации ОТР пользователю"""

    def post(self, request, *args, **kwargs):

        form = LoginForm(request.data)

        if form.is_valid():
            phone = form.cleaned_data.get("phone")
            temp = uuid.uuid4()

            try:
                user = User.objects.get(phone=phone)
            except User.DoesNotExist:
                validate_international_phonenumber(phone)
                user = User.objects.create_user(phone=phone)
                user.set_invite_code()
                user.save()
            finally:
                OTP.send_otp(phone)
                user.refresh_from_db()
                sleep(2)
                content = {
                    "phone": str(user.phone),
                    "otp": user.otp,
                    "link_for_auth": f"/api/{user.id}/{temp}/",
                }
                return Response(content, status=status.HTTP_200_OK)
        content = {"error": form.errors}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)


class LogoutAPIView(ListAPIView):
    """Контроллер для выхода из системы"""

    def get(self, request, *args, **kwargs):
        logout(request)
        content = {
            "is_auth_user": request.user.is_authenticated,
            "user": str(request.user),
            "auth": str(request.auth),
            "login_url": "/api/login/",
        }
        return Response(content, status=status.HTTP_200_OK)


class OTPAPIView(CreateAPIView):
    """Контроллер для проверки введенного ОТР и входа в систему пользователя"""

    def post(self, request, *args, **kwargs):
        phone = request.data.get("phone")
        otp = request.data.get("otp")
        otp_status = OTP.check_otp(phone, otp)

        if otp_status:
            user = authenticate(request, phone=phone)

            if user is not None:
                login(request, user, backend="user.backends.PasswordlessAuthBackend")
                content = {
                    "is_auth_user": request.user.is_authenticated,
                    "user": str(request.user),
                    "user_profile_url": f"/api/profile/",
                    "last_login": request.user.last_login,
                }
                return Response(content, status=status.HTTP_200_OK)

        else:
            content = {"error": "Не верный OTP-код!"}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)


class ProfileAPIView(ListCreateAPIView):
    """
    Контроллер для вывода информации о профиле пользователя ("GET") и добавлением пользователю инвайт-кода("POST")
    """

    def get(self, request, *args, **kwargs):
        user_id = request.session.get("_auth_user_id")

        if user_id:
            profile = User.objects.get(id=user_id)
            content = UserSerializer(profile).data
            return Response(content, status=status.HTTP_200_OK)

        else:
            content = {
                "error": "Вы не авторизованы!",
            }
            return Response(content, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, *args, **kwargs):
        code = request.data.get("invite_code")
        user_id = request.session.get("_auth_user_id")

        if user_id:
            try:
                invited_by = User.objects.get(invite_code=code)
                profile = User.objects.get(id=user_id)

                if profile.invited_by:
                    content = {
                        "error": "Вы не можете ввести новый код!",
                    }
                    return Response(content, status=status.HTTP_400_BAD_REQUEST)

                elif profile.invite_code == code:
                    content = {
                        "error": "Вы не можете ввести свой же код!",
                    }
                    return Response(content, status=status.HTTP_400_BAD_REQUEST)

                elif invited_by in profile.user_set.all():
                    content = {
                        "error": "Вы не можете ввести код того, кого вы пригласили!",
                    }
                    return Response(content, status=status.HTTP_400_BAD_REQUEST)

                else:
                    profile.invited_by = invited_by
                    profile.save()
                    content = UserSerializer(profile).data
                    return Response(content, status=status.HTTP_200_OK)

            except User.DoesNotExist:
                content = {
                    "error": "Код не существует!",
                }
                return Response(content, status=status.HTTP_400_BAD_REQUEST)

        else:
            content = {
                "error": "Вы не авторизованы!",
            }
            return Response(content, status=status.HTTP_404_NOT_FOUND)
