from django.contrib import admin
from django.urls import path, include
from stocks.views import watchlist_stocks
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("admin/", admin.site.urls),

    # API 문서
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),

    # 우리가 만든 API
    path("api/watchlist/", watchlist_stocks),
    path("api/stocks/", include("stocks.urls")),
    path("api/", include("tweets.urls")),
]