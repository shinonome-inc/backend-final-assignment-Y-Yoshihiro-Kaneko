from django.conf import settings
from django.contrib.auth import SESSION_KEY, get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import FriendShip
from tweets.models import Tweet

User = get_user_model()


class TestSignupView(TestCase):
    def setUp(self):
        self.url = reverse("accounts:signup")

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/signup.html")

    def test_success_post(self):
        valid_data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password1": "sak2ED@df#",
            "password2": "sak2ED@df#",
        }

        response = self.client.post(self.url, valid_data)

        self.assertRedirects(
            response,
            settings.LOGIN_REDIRECT_URL,
            status_code=302,
            target_status_code=200,
        )
        self.assertTrue(User.objects.filter(username=valid_data["username"]).exists())
        self.assertIn(SESSION_KEY, self.client.session)

    def test_failure_post_with_empty_form(self):
        response = self.client.post(self.url, {})
        form = response.context["form"]

        self.assertContains(
            response,
            "このフィールドは必須です。",
            count=4,
            status_code=200,
        )
        self.assertFalse(User.objects.filter(username="").exists())
        self.assertFalse(form.is_valid())

    def test_failure_post_with_empty_username(self):
        invalid_data = {
            "username": "",
            "email": "testuser@example.com",
            "password1": "sak2ED@df#",
            "password2": "sak2ED@df#",
        }

        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username=invalid_data["username"]).exists())
        self.assertFalse(form.is_valid())
        self.assertIn("このフィールドは必須です。", form.errors["username"])

    def test_failure_post_with_empty_email(self):
        invalid_data = {
            "username": "testuser",
            "email": "",
            "password1": "sak2ED@df#",
            "password2": "sak2ED@df#",
        }

        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username=invalid_data["username"]).exists())
        self.assertFalse(form.is_valid())
        self.assertIn("このフィールドは必須です。", form.errors["email"])

    def test_failure_post_with_empty_password(self):
        invalid_data = {
            "username": "testuser",
            "email": "testuser",
            "password1": "",
            "password2": "",
        }

        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username=invalid_data["username"]).exists())
        self.assertFalse(form.is_valid())
        self.assertIn("このフィールドは必須です。", form.errors["password1"])
        self.assertIn("このフィールドは必須です。", form.errors["password2"])

    def test_failure_post_with_duplicated_user(self):
        user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="qwerty123!@#",
        )

        invalid_data = {
            "username": user.username,
            "email": "aa@example.com",
            "password1": "sak2ED@df#",
            "password2": "sak2ED@df#",
        }

        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertContains(response, "同じユーザー名が既に登録済みです。", count=1, status_code=200)
        self.assertFalse(form.is_valid())
        self.assertEqual(User.objects.get(pk=user.pk), user)

    def test_failure_post_with_invalid_email(self):
        invalid_data = {
            "username": "testuser",
            "email": "invalid_email",
            "password1": "sak2ED@df#",
            "password2": "sak2ED@df#",
        }

        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertContains(response, "有効なメールアドレスを入力してください。", count=1, status_code=200)
        self.assertFalse(form.is_valid())
        self.assertFalse(User.objects.filter(username=invalid_data["username"]).exists())

    def test_failure_post_with_too_short_password(self):
        invalid_data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password1": "ak#fK1@",
            "password2": "ak#fK1@",
        }

        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertContains(
            response, "このパスワードは短すぎます。最低 8 文字以上必要です。", count=1, status_code=200
        )
        self.assertFalse(form.is_valid())
        self.assertFalse(User.objects.filter(username=invalid_data["username"]).exists())

    def test_failure_post_with_password_similar_to_username(self):
        invalid_data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password1": "testuser123",
            "password2": "testuser123",
        }

        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertContains(response, "このパスワードは ユーザー名 と似すぎています。", count=1, status_code=200)
        self.assertFalse(form.is_valid())
        self.assertFalse(User.objects.filter(username=invalid_data["username"]).exists())

    def test_failure_post_with_only_numbers_password(self):
        invalid_data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password1": "1234567890",
            "password2": "1234567890",
        }

        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertContains(response, "このパスワードは数字しか使われていません。", count=1, status_code=200)
        self.assertFalse(form.is_valid())
        self.assertFalse(User.objects.filter(username=invalid_data["username"]).exists())

    def test_failure_post_with_mismatch_password(self):
        invalid_data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password1": "asdf!@#$1234",
            "password2": "qwerq!@34^89",
        }

        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertContains(response, "確認用パスワードが一致しません。", count=1, status_code=200)
        self.assertFalse(form.is_valid())
        self.assertFalse(User.objects.filter(username=invalid_data["username"]).exists())


class TestLoginView(TestCase):
    def setUp(self):
        self.url = settings.LOGIN_URL
        self.user_data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "qwerty123!@#",
        }
        self.user = User.objects.create_user(**self.user_data)

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/login.html")

    def test_success_get_with_logged_in_user(self):
        # すでにログインしているユーザーはLOGIN_REDIRECT_URLにリダイレクト
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            settings.LOGIN_REDIRECT_URL,
            status_code=302,
            target_status_code=200,
        )

    def test_success_post(self):
        valid_data = {
            "username": self.user_data["username"],
            "password": self.user_data["password"],
        }
        response = self.client.post(self.url, valid_data)

        self.assertRedirects(
            response,
            settings.LOGIN_REDIRECT_URL,
            status_code=302,
            target_status_code=200,
        )
        self.assertIn(SESSION_KEY, self.client.session)

    def test_failure_post_with_not_exists_user(self):
        invalid_data = {
            "username": "invalid",
            "password": "invalid123!@#$",
        }
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertFalse(form.is_valid())
        self.assertContains(
            response,
            "正しいユーザー名とパスワードを入力してください。どちらのフィールドも大文字と小文字は区別されます。",
            count=1,
            status_code=200,
        )
        self.assertNotIn(SESSION_KEY, self.client.session)

    def test_failure_post_with_empty_password(self):
        invalid_data = {
            "username": self.user_data["username"],
            "password": "",
        }
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertIn("このフィールドは必須です。", form.errors["password"])
        self.assertNotIn(SESSION_KEY, self.client.session)


class TestLogoutView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="qwerty123!@#",
        )

    def test_success_post(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("accounts:logout"))
        self.assertRedirects(
            response,
            settings.LOGOUT_REDIRECT_URL,
            status_code=302,
            target_status_code=200,
        )
        self.assertNotIn(SESSION_KEY, self.client.session)


class TestUserProfileView(TestCase):
    def setUp(self):
        users = []
        for user_index in range(4):
            user = User.objects.create_user(
                username=f"user{user_index}",
                email=f"user{user_index}@example.com",
                password="asdfg!@#$%12345",
            )
            users.append(user)

            for tweet_index in range(3):
                Tweet.objects.create(user=user, body=f"tweet{tweet_index} of user{user_index}")

        self.user = users[0]
        self.user.following.add(users[1], users[2])
        self.user.followers.add(users[3])
        self.user.save()

        self.tweets = Tweet.objects.filter(user=self.user).order_by("-created_at")
        self.url = reverse("accounts:user_profile", kwargs={"username": self.user.username})

        self.client.force_login(users[1])

    def test_success_get(self):
        response = self.client.get(self.url)
        context = response.context

        self.assertEqual(response.status_code, 200)

        following_count = self.user.following.count()
        self.assertEqual(context["following_count"], following_count)
        self.assertContains(response, f"{following_count} フォロー中")
        followers_count = self.user.followers.count()
        self.assertEqual(context["followers_count"], followers_count)
        self.assertContains(response, f"{followers_count} フォロワー")

        # users[1] (loginしてるuser) は user (プロフィールのuser) をフォローしてない
        self.assertFalse(context["is_following"])
        self.assertContains(response, r'<button type="submit">フォロー</button>', html=True)

        self.assertQuerySetEqual(context["tweets"], self.tweets)
        for tweet in self.tweets:
            self.assertContains(response, tweet.body, count=1)


# class TestUserProfileEditView(TestCase):
#     def test_success_get(self):

#     def test_success_post(self):

#     def test_failure_post_with_not_exists_user(self):

#     def test_failure_post_with_incorrect_user(self):


class TestFollowView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="user",
            email="user@example.com",
            password="asdfg!@#$%12345",
        )
        self.following_user = User.objects.create_user(
            username="Elon Mask",
            email="elon@example.com",
            password="asdfg!@#$%22345",
        )
        self.url = lambda username: reverse("accounts:follow", kwargs={"username": username})
        self.client.force_login(self.user)

    def test_success_post(self):
        response = self.client.post(self.url(self.following_user.username))
        self.assertRedirects(
            response,
            reverse("tweets:home"),
            status_code=302,
            target_status_code=200,
        )
        self.assertTrue(
            FriendShip.objects.filter(
                follower=self.user,
                followee=self.following_user,
            ).exists()
        )

    def test_failure_post_with_not_exist_user(self):
        response = self.client.post(self.url("not_exist_user"))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(FriendShip.objects.count(), 0)

    def test_failure_post_with_self(self):
        response = self.client.post(self.url(self.user.username))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(FriendShip.objects.count(), 0)


class TestUnfollowView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="user",
            email="user@example.com",
            password="asdfg!@#$%12345",
        )
        self.following_user = User.objects.create_user(
            username="Elon Mask",
            email="elon@example.com",
            password="asdfg!@#$%22345",
        )
        self.user.following.add(self.following_user)
        self.url = lambda username: reverse("accounts:unfollow", kwargs={"username": username})
        self.client.force_login(self.user)

    def test_success_post(self):
        response = self.client.post(self.url(self.following_user.username))
        self.assertRedirects(
            response,
            reverse("tweets:home"),
            status_code=302,
            target_status_code=200,
        )
        self.assertFalse(
            FriendShip.objects.filter(
                follower=self.user,
                followee=self.following_user,
            ).exists()
        )

    def test_failure_post_with_not_exist_user(self):
        response = self.client.post(self.url("not_exist_user"))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(
            FriendShip.objects.filter(
                follower=self.user,
                followee=self.following_user,
            ).exists()
        )

    def test_failure_post_with_self(self):
        response = self.client.post(self.url(self.user.username))
        self.assertEqual(response.status_code, 400)
        self.assertTrue(
            FriendShip.objects.filter(
                follower=self.user,
                followee=self.following_user,
            ).exists()
        )


class TestFollowingListView(TestCase):
    def setUp(self):
        self.users = []
        for user_index in range(4):
            user = User.objects.create_user(
                username=f"user{user_index}",
                email=f"user{user_index}@example.com",
                password="asdfg!@#$%12345",
            )
            self.users.append(user)

        self.user = self.users[0]
        self.url = reverse("accounts:following_list", kwargs={"username": self.user.username})
        self.expected_following = [self.users[2], self.users[1], self.users[3]]
        for i, followee in enumerate(self.expected_following):
            created_at = timezone.now() - timezone.timedelta(minutes=i * 10)
            FriendShip.objects.create(follower=self.user, followee=followee, created_at=created_at)

        self.client.force_login(self.users[2])

    def test_success_get(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        for user in self.expected_following:
            self.assertContains(response, user.username, count=1, html=True)

        # following_list は (user, created_at) のリスト
        actual_following = [user for (user, _) in response.context["following_list"]]
        self.assertQuerysetEqual(actual_following, self.expected_following, ordered=True)
        self.assertTemplateUsed("accounts/following_list.html")


class TestFollowerListView(TestCase):
    def setUp(self):
        self.users = []
        for user_index in range(4):
            user = User.objects.create_user(
                username=f"user{user_index}",
                email=f"user{user_index}@example.com",
                password="asdfg!@#$%12345",
            )
            self.users.append(user)

        self.user = self.users[0]
        self.url = reverse("accounts:follower_list", kwargs={"username": self.user.username})
        self.expected_followers = [self.users[2], self.users[1], self.users[3]]
        for i, follower in enumerate(self.expected_followers):
            created_at = timezone.now() - timezone.timedelta(minutes=i * 10)
            FriendShip.objects.create(follower=follower, followee=self.user, created_at=created_at)

        self.client.force_login(self.users[2])

    def test_success_get(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        for follower in self.expected_followers:
            self.assertContains(response, follower.username, count=1, html=True)

        # follower_list は (user, created_at) のリスト
        actual_followers = [user for (user, _) in response.context["follower_list"]]
        self.assertQuerysetEqual(actual_followers, self.expected_followers, ordered=True)
        self.assertTemplateUsed("accounts/follower_list.html")
