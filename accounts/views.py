from django.conf import settings
from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponseRedirect, JsonResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, View
from django.views.generic.detail import SingleObjectMixin

from tweets.models import Tweet

from .forms import SignupForm

User = get_user_model()


class SignupView(CreateView):
    form_class = SignupForm
    template_name = "accounts/signup.html"
    success_url = settings.LOGIN_REDIRECT_URL

    def form_valid(self, form):
        response = super().form_valid(form)
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password1"]

        user = authenticate(self.request, username=username, password=password)
        login(self.request, user)
        return response


class UserProfileView(LoginRequiredMixin, DetailView):
    model = User
    slug_field = "username"
    slug_url_kwarg = "username"
    context_object_name = "user_profile"
    template_name = "accounts/user_profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = context["user_profile"]
        context["is_following"] = self.request.user.following.filter(pk=user.pk).exists()
        context["tweets"] = Tweet.objects.select_related("user").filter(user=user).order_by("-created_at")
        return context


class FollowView(LoginRequiredMixin, SingleObjectMixin, View):
    model = User
    slug_field = "username"
    slug_url_kwarg = "username"
    next_page = reverse_lazy("tweets:home")

    def post(self, request, *args, **kwargs):
        try:
            target_user = self.get_object()
        except Http404:
            response = JsonResponse({"message": "指定されたユーザーは存在しません"})
            response.status_code = 404
            return response
        if target_user == request.user:
            response = JsonResponse({"message": "この操作は自分に対しては行えません"})
            response.status_code = 400
            return response

        request.user.following.add(target_user)
        request.user.save()
        return HttpResponseRedirect(self.next_page)


class UnFollowView(LoginRequiredMixin, SingleObjectMixin, View):
    model = User
    slug_field = "username"
    slug_url_kwarg = "username"
    next_page = reverse_lazy("tweets:home")

    def post(self, request, *args, **kwargs):
        try:
            target_user = self.get_object()
        except Http404:
            response = JsonResponse({"message": "指定されたユーザーは存在しません"})
            response.status_code = 404
            return response
        if target_user == request.user:
            response = JsonResponse({"message": "この操作は自分に対しては行えません"})
            response.status_code = 400
            return response

        request.user.following.remove(target_user)
        request.user.save()
        return HttpResponseRedirect(self.next_page)
