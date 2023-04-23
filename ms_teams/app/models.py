import jwt
import datetime
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
# Create your models here.


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


class Event(models.Model):
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f'{self.name} ({self.type.name}): {self.start_date} - {self.end_date}'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'is_active': self.is_active,
        }

    def get_image_url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        return None


class Team(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(
        upload_to='images/teams/', null=True, blank=True)
    leader = models.ForeignKey(
        ManuscriptUser, on_delete=models.CASCADE, blank=False, null=False, default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    members = models.ManyToManyField(ManuscriptUser, related_name='members')
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name

    def get_members(self):
        return self.members.all()

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'leader': self.leader.to_dict(),
            'members': [member.to_dict() for member in self.members.all()],
            'event': self.event.to_dict(),
            'is_active': self.is_active,
        }
