from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Stock, StockTrendStat, StockChartPoint


def get_price_or_none(stock):
    try:
        return stock.price
    except Exception:
        return None


@api_view(["GET"])
def trending_stocks(request):
    stats = StockTrendStat.objects.select_related("stock").all()[:10]

    data = []

    for index, stat in enumerate(stats, start=1):
        stock = stat.stock
        price = get_price_or_none(stock)

        data.append({
            "rank": index,
            "name": stock.name,
            "ticker": stock.ticker,
            "market": stock.market,
            "logo_url": stock.logo_url,
            "tweet_volume": stat.tweet_volume,
            "one_hour_change_rate": float(stat.one_hour_change_rate),
            "current_price": float(price.current_price) if price else None,
            "currency": price.currency if price else None,
            "price_change_rate": float(price.change_rate) if price else None,
            "price_change_amount": float(price.change_amount) if price else None,
            "updated_at": stat.updated_at,
        })

    return Response(data)


@api_view(["GET"])
def stock_detail(request, ticker):
    stock = get_object_or_404(Stock, ticker__iexact=ticker)
    price = get_price_or_none(stock)

    data = {
        "name": stock.name,
        "ticker": stock.ticker,
        "market": stock.market,
        "logo_url": stock.logo_url,
        "current_price": float(price.current_price) if price else None,
        "currency": price.currency if price else None,
        "change_rate": float(price.change_rate) if price else None,
        "change_amount": float(price.change_amount) if price else None,
        "volume": price.volume if price else None,
        "updated_at": price.updated_at if price else None,
    }

    return Response(data)


@api_view(["GET"])
def stock_chart(request, ticker):
    stock = get_object_or_404(Stock, ticker__iexact=ticker)

    points = StockChartPoint.objects.filter(stock=stock).order_by("time")[:200]

    data = [
        {
            "time": point.time,
            "price": float(point.price),
            "volume": point.volume,
        }
        for point in points
    ]

    return Response(data)

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

    data = []

    for stock in stocks:
        price = get_price_or_none(stock)

        data.append({
            "name": stock.name,
            "ticker": stock.ticker,
            "market": stock.market,
            "logo_url": stock.logo_url,
            "current_price": float(price.current_price) if price else None,
            "currency": price.currency if price else None,
            "price_change_rate": float(price.change_rate) if price else None,
        })

    return Response(data)