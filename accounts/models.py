from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse


class User(AbstractUser):
    email = models.EmailField()

    def get_absolute_url(self):
        return reverse("accounts:user_profile", kwargs={"username": self.username})


# class FriendShip(models.Model):
