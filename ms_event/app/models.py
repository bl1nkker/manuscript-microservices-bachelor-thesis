from django.db import models
from django.contrib.auth.models import User
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


class Event(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(
        upload_to='uploads/images/events/', null=True, blank=True)

    location = models.CharField(max_length=100, default='Almaty, Kazakhstan')
    location_url = models.URLField(blank=True, default='')
    description = models.TextField(blank=True)
    full_description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(ManuscriptUser, on_delete=models.CASCADE)
    tags = models.JSONField(default=list)

    def __str__(self) -> str:
        return f'{self.name} ({self.type.name}): {self.start_date} - {self.end_date}'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'image': self.image.url if self.image else None,
            'location': self.location,
            'location_url': self.location_url,
            'description': self.description,
            'full_description': self.full_description,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'author': self.author.to_dict(),
            'tags': self.tags,
        }
