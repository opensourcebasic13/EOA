from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Stock, StockTrendStat, StockChartPoint, Watchlist
from .serializers import (
    StockSummarySerializer,
    StockDetailSerializer,
    StockTrendStatSerializer,
    StockChartPointSerializer,
)


@api_view(["GET"])
def trending_stocks(request):
    stats = list(
        StockTrendStat.objects
        .select_related("stock")
        .all()[:10]
    )

    rank_map = {
        stat.id: index
        for index, stat in enumerate(stats, start=1)
    }

    serializer = StockTrendStatSerializer(
        stats,
        many=True,
        context={"rank_map": rank_map}
    )

    return Response(serializer.data)


@api_view(["GET"])
def search_stocks(request):
    query = request.GET.get("q", "").strip()

    if not query:
        return Response([])

    stocks = Stock.objects.filter(
        Q(name__icontains=query) |
        Q(ticker__icontains=query) |
        Q(market__icontains=query)
    )[:10]

    serializer = StockSummarySerializer(stocks, many=True)

    return Response(serializer.data)


@api_view(["GET"])
def watchlist_stocks(request):
    if request.user.is_authenticated:
        watchlists = Watchlist.objects.filter(user=request.user).select_related("stock")
        stocks = [item.stock for item in watchlists]
    else:
        stats = StockTrendStat.objects.select_related("stock").all()[:5]
        stocks = [stat.stock for stat in stats]

        if not stocks:
            stocks = Stock.objects.all()[:5]

    serializer = StockSummarySerializer(stocks, many=True)

    return Response(serializer.data)


@api_view(["GET"])
def stock_detail(request, ticker):
    stock = get_object_or_404(Stock, ticker__iexact=ticker)

    serializer = StockDetailSerializer(stock)

    return Response(serializer.data)


@api_view(["GET"])
def stock_chart(request, ticker):
    stock = get_object_or_404(Stock, ticker__iexact=ticker)

    points = StockChartPoint.objects.filter(stock=stock).order_by("time")[:200]

    serializer = StockChartPointSerializer(points, many=True)

    return Response(serializer.data)