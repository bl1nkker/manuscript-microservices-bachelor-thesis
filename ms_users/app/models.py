import jwt
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class ManuscriptUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self) -> str:
        return self.user.username

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.user.username,
            'email': self.user.email,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'phone_number': self.phone_number,
            'description': self.description,
        }

    def generate_jwt_token(self):
        token = jwt.encode({
            "id": self.id,
            "email": self.user.email,
        }, settings.TOKEN_SECRET, algorithm='HS256')

        return token
