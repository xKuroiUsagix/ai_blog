from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    auto_post_reply = models.TimeField(null=True, blank=True)
