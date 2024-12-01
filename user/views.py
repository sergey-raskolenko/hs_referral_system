from time import sleep

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout

from .forms import  LoginForm
from user.models import User
from .services import OTP
from django.contrib import messages
import uuid



def login_page(request):
	"""Контроллер для авторизации или регистрации пользователя, с перенаправлением на подтверждение ОТР"""
	form = LoginForm(request.POST or None)
	context = {
		"form": form,
		"title": "Authorization"
	}
	if form.is_valid():
		phone = form.cleaned_data.get('phone')
		temp = uuid.uuid4()

		try:
			user = User.objects.get(phone=phone)
		except User.DoesNotExist:
			user = User.objects.create_user(phone=phone)
			user.set_invite_code()
			user.save()
		finally:
			OTP.send_otp(phone)
			sleep(2)
			return redirect(f"/otp/{user.id}/{temp}")

	return render(request, template_name="login.html", context=context)

def logout_view(request):
	"""Контроллер для выхода из системы"""
	logout(request)
	return redirect("login/")


def generate_otp(request, pk, uuid):
	"""Контроллер для ввода ОТР"""
	context = {
		"title": "OTP checking"
	}
	return render(request, template_name='otp.html', context=context)


def check_otp(request):
	"""Контроллер для проверки ОТР"""
	otp = request.POST.get("secret")
	phone = request.POST.get("phone")
	otp_status = OTP.check_otp(phone, otp)

	if otp_status:
		user = authenticate(request, phone=phone)

		if user is not None:
			login(request, user, backend='user.backends.PasswordlessAuthBackend')
			return redirect(f"/{user.invite_code}")

	else:
		messages.error(request, "Не верный OTP-код!")

	return render(request, "otp.html")


def profile_page(request, invite_code):
	"""Контроллер для вывода профиля пользователя"""
	profile = get_object_or_404(User, invite_code=invite_code)
	context = {
		"title": f"Профиль: {profile.phone}",
		"profile": profile
	}
	return render(request, template_name="profile.html", context=context)


def enter_invite_code(request, invite_code):
	"""Контроллер для добавления пользователю инвайт-кода"""
	code = request.POST.get("code")
	try:
		invited_by = User.objects.get(invite_code=code)
		profile = User.objects.get(invite_code=invite_code)

		if profile.invited_by:
			messages.error(request, "Вы не можете ввести новый код!")

		elif profile.invite_code == code:
			messages.error(request, "Вы не можете ввести свой же код!")

		elif invited_by in profile.user_set.all():
			messages.error(request, "Вы не можете ввести код того, кого вы пригласили!")

		else:
			profile.invited_by = invited_by
			profile.save()

	except User.DoesNotExist:
		messages.error(request, "Код не существует!")

	return redirect(f"/{invite_code}")



