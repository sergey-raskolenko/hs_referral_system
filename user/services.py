import random
from time import sleep
from user.models import User


class OTP:
	"""Класс для работы с одноразовыми паролями"""

	@classmethod
	def send_otp(cls, phone):
		"""
		Класс-метод для отправки ОТР пользователю
		"""
		otp = str(random.randint(1000, 9999))
		user = User.objects.get(phone=phone)
		user.otp = otp
		user.save()
		sleep(2)
		print(f"OTP:{otp}")

	@staticmethod
	def check_otp(phone, otp):
		"""
		Статический метод для проверки ОТР
		"""
		user = User.objects.get(phone=phone)
		if user.otp == otp:
			return True
		return False
