from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from tweets.models import Tweet

User = get_user_model()


class TestHomeView(TestCase):
    def setUp(self):
        self.url = reverse("tweets:home")

        for user_index in range(3):
            user = User.objects.create_user(
                username=f"user{user_index}",
                email=f"user{user_index}@example.com",
                password="asdfg!@#$%12345",
            )

            for tweet_index in range(3):
                Tweet.objects.create(user=user, body=f"tweet{tweet_index} of user{user_index}")
        self.all_tweets = Tweet.objects.select_related("user").order_by("-created_at").all()

        user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="asdf!@#$1234",
        )
        self.client.force_login(user)

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertContains(response, "によるツイート", count=len(self.all_tweets), status_code=200)
        self.assertTemplateUsed(response, "tweets/home.html")
        self.assertQuerySetEqual(response.context["tweet_list"], self.all_tweets)


class TestTweetCreateView(TestCase):
    def setUp(self):
        self.url = reverse("tweets:create")
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="asdf!@#$1234",
        )
        self.client.force_login(self.user)

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tweets/create.html")

    def test_success_post(self):
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
    def setUp(self):
        user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="asdf!@#$1234",
        )
        self.tweet = Tweet.objects.create(user=user, body="This is test Tweet.")
        self.client.force_login(user)
        self.url = reverse("tweets:detail", kwargs={"pk": self.tweet.pk})

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertContains(response, self.tweet.body, count=1, status_code=200)
        self.assertTemplateUsed(response, "tweets/detail.html")
        self.assertQuerysetEqual([response.context["object"]], [self.tweet])


class TestTweetDeleteView(TestCase):
    def setUp(self):
        self.get_url = lambda pk: reverse("tweets:delete", kwargs={"pk": pk})
        user = User.objects.create_user(
            username="user1",
            email="user1@example.com",
            password="asdfg!@#$%12345",
        )
        self.tweet = Tweet.objects.create(user=user, body="tweet of user1")

        another_user = User.objects.create_user(
            username="user2",
            email="user2@example.com",
            password="asdfg!@#$%12345",
        )
        self.anothers_tweet = Tweet.objects.create(user=another_user, body="tweet of user2")

        self.client.force_login(user)

    def test_success_post(self):
        response = self.client.post(self.get_url(self.tweet.pk))
        self.assertRedirects(
            response,
            reverse("tweets:home"),
            status_code=302,
            target_status_code=200,
        )
        self.assertFalse(Tweet.objects.filter(pk=self.tweet.pk).exists())
        self.assertTrue(Tweet.objects.filter(pk=self.anothers_tweet.pk).exists())

    def test_failure_post_with_not_exist_tweet(self):
        response = self.client.post(self.get_url(100))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(len(Tweet.objects.all()), 2)

    def test_failure_post_with_incorrect_user(self):
        response = self.client.post(self.get_url(self.anothers_tweet.pk))
        self.assertEqual(response.status_code, 403)
        self.assertEqual(len(Tweet.objects.all()), 2)


class TestLikeView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="hoge",
            email="hoge@example.com",
            password="asdfg!@#$%12345",
        )
        self.tweet = Tweet.objects.create(user=self.user, body="foo")
        self.get_url = lambda pk: reverse("tweets:like", kwargs={"pk": pk})
        self.client.force_login(self.user)

    def test_success_post(self):
        url = self.get_url(self.tweet.pk)
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.tweet.like_users.filter(pk=self.user.pk).exists())

    def test_failure_post_with_not_exist_tweet(self):
        url = self.get_url(100)
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            self.tweet.like_users.through.objects.all().count(),
            0,
        )

    def test_failure_post_with_liked_tweet(self):
        self.tweet.like_users.add(self.user)
        self.tweet.save()

        url = self.get_url(self.tweet.pk)
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            self.tweet.like_users.through.objects.all().count(),
            1,
        )


class TestUnLikeView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="hoge",
            email="hoge@example.com",
            password="asdfg!@#$%12345",
        )
        self.tweet = Tweet.objects.create(user=self.user, body="foo")
        self.tweet.like_users.add(self.user)
        self.tweet.save()
        self.get_url = lambda pk: reverse("tweets:unlike", kwargs={"pk": pk})
        self.client.force_login(self.user)

    def test_success_post(self):
        url = self.get_url(self.tweet.pk)
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.tweet.like_users.count(), 0)

    def test_failure_post_with_not_exist_tweet(self):
        url = self.get_url(100)
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            self.tweet.like_users.through.objects.all().count(),
            1,
        )

    def test_failure_post_with_unliked_tweet(self):
        self.tweet.like_users.remove(self.user)
        self.tweet.save()

        url = self.get_url(self.tweet.pk)
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            self.tweet.like_users.through.objects.all().count(),
            0,
        )
