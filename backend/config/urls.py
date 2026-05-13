from django.contrib import admin
from django.urls import path, include
from stocks import views as stock_views


urlpatterns = [
    path("admin/", admin.site.urls),

    path("api/watchlist/", stock_views.watchlist_stocks),

    path("api/stocks/", include("stocks.urls")),
    path("api/", include("tweets.urls")),
]
