from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class TestHomeView(TestCase):
    def test_success_get(self):
        user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="asdf!@#$1234",
        )
        self.client.force_login(user)

        response = self.client.get(reverse("tweets:home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tweets/home.html")


# class TestTweetCreateView(TestCase):
#     def test_success_get(self):

#     def test_success_post(self):

#     def test_failure_post_with_empty_content(self):

#     def test_failure_post_with_too_long_content(self):


# class TestTweetDetailView(TestCase):
#     def test_success_get(self):


# class TestTweetDeleteView(TestCase):
#     def test_success_post(self):

#     def test_failure_post_with_not_exist_tweet(self):

#     def test_failure_post_with_incorrect_user(self):


# class TestLikeView(TestCase):
#     def test_success_post(self):

#     def test_failure_post_with_not_exist_tweet(self):

#     def test_failure_post_with_liked_tweet(self):


# class TestUnLikeView(TestCase):

#     def test_success_post(self):

#     def test_failure_post_with_not_exist_tweet(self):

#     def test_failure_post_with_unliked_tweet(self):
