# Generated by Django 4.2.16 on 2024-11-29 05:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0002_friendship_user_following"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="friendship",
            constraint=models.UniqueConstraint(fields=("follower", "followee"), name="unique_friendship"),
        ),
    ]
