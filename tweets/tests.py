from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from tweets.models import Tweet

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


class TestTweetCreateView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="asdf!@#$1234",
        )
        self.url = reverse("tweets:create")

    def test_success_get(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tweets/create.html")

    def test_success_post(self):
        self.client.force_login(self.user)

        valid_data = {"body": "Tweet"}
        response = self.client.post(self.url, valid_data)

        self.assertRedirects(
            response,
            reverse("tweets:home"),
            status_code=302,
            target_status_code=200,
        )
        self.assertTrue(Tweet.objects.filter(user=self.user).filter(body=valid_data["body"]).exists())

    def test_failure_post_with_empty_content(self):
        self.client.force_login(self.user)

        invalid_data = {"body": ""}
        response = self.client.post(self.url, invalid_data)

        self.assertContains(
            response,
            "このフィールドは必須です",
            count=1,
            status_code=200,
        )
        self.assertEqual(len(Tweet.objects.all()), 0)

    def test_failure_post_with_too_long_content(self):
        self.client.force_login(self.user)

        invalid_data = {"body": "T" * 141}
        response = self.client.post(self.url, invalid_data)

        self.assertContains(
            response,
            "この値は 140 文字以下でなければなりません( 141 文字になっています)。",
            count=1,
            status_code=200,
        )
        self.assertEqual(len(Tweet.objects.all()), 0)


class TestTweetDetailView(TestCase):
    def test_success_get(self):
        user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="asdf!@#$1234",
        )
        self.client.force_login(user)
        tweet = Tweet.objects.create(user=user, body="This is test Tweet.")

        response = self.client.get(reverse("tweets:detail", kwargs={"pk": tweet.pk}))
        self.assertContains(response, tweet.body, count=1, status_code=200)
        self.assertTemplateUsed(response, "tweets/detail.html")
        self.assertQuerysetEqual([response.context["object"]], [tweet])


class TestTweetDeleteView(TestCase):
    def setUp(self):
        self.url = lambda pk: reverse("tweets:delete", kwargs={"pk": pk})
        self.user1 = User.objects.create_user(
            username="user1",
            email="user1@example.com",
            password="asdfg!@#$%12345",
        )
        self.tweet1 = Tweet.objects.create(user=self.user1, body="tweet of user1")

        self.user2 = User.objects.create_user(
            username="user2",
            email="user2@example.com",
            password="asdfg!@#$%12345",
        )
        self.tweet2 = Tweet.objects.create(user=self.user2, body="tweet of user2")

    def test_success_post(self):
        self.client.force_login(self.user1)
        response = self.client.post(self.url(1))

        self.assertRedirects(
            response,
            reverse("tweets:home"),
            status_code=302,
            target_status_code=200,
        )
        self.assertFalse(Tweet.objects.filter(pk=1).exists())

    def test_failure_post_with_not_exist_tweet(self):
        self.client.force_login(self.user1)
        response = self.client.post(self.url(100))

        self.assertEqual(response.status_code, 404)
        self.assertEqual(len(Tweet.objects.all()), 2)

    def test_failure_post_with_incorrect_user(self):
        self.client.force_login(self.user1)
        response = self.client.post(self.url(2))

        self.assertEqual(response.status_code, 403)
        self.assertEqual(len(Tweet.objects.all()), 2)


# class TestLikeView(TestCase):
#     def test_success_post(self):

#     def test_failure_post_with_not_exist_tweet(self):

#     def test_failure_post_with_liked_tweet(self):


# class TestUnLikeView(TestCase):

#     def test_success_post(self):

#     def test_failure_post_with_not_exist_tweet(self):

#     def test_failure_post_with_unliked_tweet(self):
