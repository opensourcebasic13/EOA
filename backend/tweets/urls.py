from django.urls import path
from . import views

urlpatterns = [
    path("stocks/<str:ticker>/tweets/hot/", views.hot_tweets),
]