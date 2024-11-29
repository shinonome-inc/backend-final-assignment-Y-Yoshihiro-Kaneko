from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils import timezone


class User(AbstractUser):
    email = models.EmailField()
    following = models.ManyToManyField(
        "self",
        related_name="followers",
        symmetrical=False,
        through="FriendShip",
        through_fields=("follower", "followee"),
    )

    def get_absolute_url(self):
        return reverse("accounts:user_profile", kwargs={"username": self.username})


class FriendShip(models.Model):
    # フォローしている人
    follower = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="+", on_delete=models.CASCADE)
    # フォローされている人
    followee = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="+", on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["follower", "followee"], name="unique_friendship")]
