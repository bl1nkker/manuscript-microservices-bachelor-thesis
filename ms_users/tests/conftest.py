import datetime
import string
import random

from django.contrib.auth.models import User
from django.test import Client


def login(c: Client, username="testuser"):
    c.force_login(User.objects.get(username=username))
