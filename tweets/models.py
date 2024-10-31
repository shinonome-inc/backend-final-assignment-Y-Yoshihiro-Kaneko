from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse

User = get_user_model()


class Tweet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    body = models.TextField(max_length=140)

    def __str__(self):
        return f"{self.user.username}'s post"

    def get_absolute_url(self):
        return reverse("tweets:detail", kwargs={"pk": self.pk})
