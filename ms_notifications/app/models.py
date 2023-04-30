import jwt
import datetime
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
import core.constants as constants


class ManuscriptUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.user.username

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.user.username,
            'email': self.user.email,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
        }

    def generate_jwt_token(self):
        token = jwt.encode({
            "id": self.id,
            "email": self.user.email,
        }, settings.SECRET_KEY, algorithm='HS256')

        return token

    @property
    def username(self):
        return self.user.username
# Create your models here.


class Notification(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(ManuscriptUser, on_delete=models.CASCADE)
    message = models.CharField(max_length=100)
    status = models.CharField(max_length=20, default=constants.SUCCESS_TYPE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
