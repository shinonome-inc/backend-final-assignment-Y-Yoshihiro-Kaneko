from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import Http404
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, View
from django.views.generic.edit import SingleObjectMixin

from tweets.models import Tweet


class HomeView(LoginRequiredMixin, ListView):
    template_name = "tweets/home.html"
    queryset = Tweet.objects.select_related("user").prefetch_related("like_users").order_by("-created_at")


class TweetCreateView(LoginRequiredMixin, CreateView):
    template_name = "tweets/create.html"
    model = Tweet
    fields = ("body",)
    success_url = reverse_lazy("tweets:home")

    def form_valid(self, form):
        tweet = form.save(commit=False)
        tweet.user = self.request.user
        tweet.save()
        self.object = tweet
        return HttpResponseRedirect(self.get_success_url())


class TweetDetailView(LoginRequiredMixin, DetailView):
    template_name = "tweets/detail.html"
    model = Tweet


class TweetDeleteView(UserPassesTestMixin, DeleteView):
    template_name = "tweets/delete.html"
    success_url = reverse_lazy("tweets:home")
    model = Tweet

    def test_func(self):
        tweet = self.get_object()
        if tweet.user == self.request.user:
            return True


class TweetLikeView(LoginRequiredMixin, SingleObjectMixin, View):
    model = Tweet

    def like(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
        except Http404:
            response = JsonResponse({"message": "このツイートは存在しません"})
            response.status_code = 404
            return response

        self.object.like_users.add(request.user)
        self.object.save()
        return JsonResponse({"message": "ok"})

    def post(self, request, *args, **kwargs):
        return self.like(request, *args, **kwargs)


class TweetUnlikeView(LoginRequiredMixin, SingleObjectMixin, View):
    model = Tweet

    def unlike(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
        except Http404:
            response = JsonResponse({"message": "このツイートは存在しません"})
            response.status_code = 404
            return response

        self.object.like_users.remove(request.user)
        self.object.save()
        return JsonResponse({"message": "ok"})

    def post(self, request, *args, **kwargs):
        return self.unlike(request, *args, **kwargs)
