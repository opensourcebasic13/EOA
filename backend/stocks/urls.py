from django.urls import path
from . import views

urlpatterns = [
    path("search/", views.search_stocks),
    path("trending/", views.trending_stocks),

    path("<str:ticker>/chart/", views.stock_chart),
    path("<str:ticker>/analysis/", views.stock_ai_analysis),
    path("<str:ticker>/overview/", views.stock_overview),

    path("<str:ticker>/", views.stock_detail),
]