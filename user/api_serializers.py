from rest_framework import serializers
from user.models import User


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для объекта модели User"""

    invited_followers = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()

    @staticmethod
    def get_phone(instance):
        return str(instance.phone)

    @staticmethod
    def get_invited_followers(instance):
        return [str(user) for user in instance.user_set.all()]

    class Meta:
        model = User
        fields = ["id", "phone", "invite_code", "invited_by", "invited_followers"]
