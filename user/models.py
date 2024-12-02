from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.db import models
from django.contrib.auth.base_user import BaseUserManager
import random
import string

NULLABLE = {"null": True, "blank": True}


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_superuser(self, phone, password, **other_fields):
        """
        Метод для создания суперпользователя с переданными телефоном и паролем
        """
        other_fields.setdefault("is_staff", True)
        other_fields.setdefault("is_superuser", True)
        other_fields.setdefault("is_active", True)

        if other_fields.get("is_staff") is not True:
            raise ValueError("Superuser must be assigned to is_staff=True")
        if other_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must be assigned to is_superuser=True")

        user = self.create_user(phone, password, **other_fields)
        user.set_password(password)
        user.save()
        return user

    def create_user(self, phone, password=None, **other_fields):
        """Метод для создания пользователя"""
        if not phone:
            raise ValueError("Phone is required!")
        if password is not None:
            user = self.model(phone=phone, password=password, **other_fields)
            user.save()
        else:
            user = self.model(phone=phone, **other_fields)
            user.set_unusable_password()
            user.save()
        return user


class User(AbstractUser, PermissionsMixin):
    """Модель для описания пользователя"""

    objects = UserManager()

    username = None

    phone = PhoneNumberField(max_length=30, verbose_name="phone", unique=True)
    invite_code = models.CharField(
        max_length=6,
        verbose_name="invite code",
    )
    invited_by = models.ForeignKey(
        to="self", on_delete=models.CASCADE, verbose_name="invited by", **NULLABLE
    )
    otp = models.CharField(max_length=4, verbose_name="otp", **NULLABLE)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"
        db_table = "users"
        ordering = ["id"]

    def __str__(self):
        return str(self.phone)

    def set_invite_code(self):
        """Метод устанавливает уникальный инвайт-код для данного пользователя"""
        if not self.invite_code:
            while True:
                invite_code = "".join(
                    random.choices(string.ascii_letters + string.digits, k=6)
                )
                if not User.objects.filter(invite_code=invite_code).exists():
                    self.invite_code = invite_code
                    break
