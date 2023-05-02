import jwt
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
import core.constants as constants
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
        }, settings.TOKEN_SECRET, algorithm='HS256')

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
    created_at = models.DateTimeField(auto_now_add=True)
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
            'event': self.event.to_dict(),
            'is_active': self.is_active,
        }


class Participant(models.Model):
    user = models.ForeignKey(ManuscriptUser, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    role = models.CharField(
        max_length=10, default=constants.MEMBER_ROLE)
    status = models.CharField(
        max_length=100, default=constants.PENDING_STATUS)

    def __str__(self) -> str:
        return f'{self.user} - {self.team}'

    def to_dict(self):
        return {
            'id': self.id,
            'user': self.user.to_dict(),
            'team': self.team.to_dict(),
            'role': self.role,
            'status': self.status,
        }
