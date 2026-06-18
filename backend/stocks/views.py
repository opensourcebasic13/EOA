from django.db.models import Q
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from tweets.models import TweetPost
from .models import Stock, StockTrendStat, StockChartPoint, Watchlist, StockAiAnalysis
from .serializers import (
    StockSummarySerializer,
    StockDetailSerializer,
    StockTrendStatSerializer,
    StockChartPointSerializer,
    StockAiAnalysisSerializer,
)


@api_view(["GET"])
def trending_stocks(request):
    stats = list(
        StockTrendStat.objects
        .select_related("stock")
        .all()[:20]
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
    )[:20]

    serializer = StockSummarySerializer(stocks, many=True)

    return Response(serializer.data)


@api_view(["GET", "POST", "DELETE"])
def watchlist_stocks(request):
    # 관심 주식 조회
    if request.method == "GET":
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

    # 추가/삭제는 로그인 필요
    if not request.user.is_authenticated:
        return Response(
            {
                "success": False,
                "message": "로그인이 필요합니다.",
                "data": None,
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )

    ticker = request.data.get("ticker", "").strip().upper()

    if not ticker:
        return Response(
            {
                "success": False,
                "message": "ticker가 필요합니다.",
                "data": None,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    stock = get_object_or_404(Stock, ticker__iexact=ticker)

    # 관심 주식 추가
    if request.method == "POST":
        Watchlist.objects.get_or_create(
            user=request.user,
            stock=stock,
        )

        return Response({
            "success": True,
            "message": f"{ticker}가 관심 주식에 추가되었습니다.",
            "data": {
                "ticker": stock.ticker,
                "name": stock.name,
                "market": stock.market,
            },
        })

    # 관심 주식 삭제
    if request.method == "DELETE":
        Watchlist.objects.filter(
            user=request.user,
            stock=stock,
        ).delete()

        return Response({
            "success": True,
            "message": f"{ticker}가 관심 주식에서 삭제되었습니다.",
            "data": {
                "ticker": stock.ticker,
                "name": stock.name,
                "market": stock.market,
            },
        })


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


@api_view(["GET", "POST"])
def stock_ai_analysis(request, ticker):
    stock = get_object_or_404(Stock, ticker__iexact=ticker)

    if request.method == "GET":
        try:
            analysis = stock.ai_analysis
        except StockAiAnalysis.DoesNotExist:
            return Response(
                {
                    "success": False,
                    "message": "AI 분석 결과가 아직 없습니다.",
                    "data": None,
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = StockAiAnalysisSerializer(analysis)

        return Response({
            "success": True,
            "message": "AI 분석 결과를 조회했습니다.",
            "data": serializer.data,
        })

    sentiment_scores = request.data.get("sentiment_scores", {})
    model_info = request.data.get("model_info", {})

    analysis, _ = StockAiAnalysis.objects.update_or_create(
        stock=stock,
        defaults={
            "summary": request.data.get("summary", ""),
            "summary_ko": request.data.get("summary_ko", ""),
            "main_sentiment": request.data.get("main_sentiment", "neutral"),
            "positive_score": sentiment_scores.get("positive", 0),
            "negative_score": sentiment_scores.get("negative", 0),
            "neutral_score": sentiment_scores.get("neutral", 0),
            "keywords": request.data.get("keywords", []),
            "summary_model": model_info.get("summary_model", "mT5"),
            "sentiment_model": model_info.get("sentiment_model", "FinBERT"),
        }
    )

    serializer = StockAiAnalysisSerializer(analysis)

    return Response(
        {
            "success": True,
            "message": "AI 분석 결과가 저장되었습니다.",
            "data": serializer.data,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET"])
def stock_overview(request, ticker):
    stock = get_object_or_404(Stock, ticker__iexact=ticker)

    try:
        price = stock.price
    except Exception:
        price = None

    try:
        trend_stat = stock.trend_stat
    except Exception:
        trend_stat = None

    chart_points = StockChartPoint.objects.filter(stock=stock).order_by("time")[:200]

    tweets = TweetPost.objects.filter(stock=stock).order_by(
        "-is_hot",
        "-like_count",
        "-repost_count",
        "-posted_at"
    )[:20]

    try:
        ai_analysis = stock.ai_analysis
    except StockAiAnalysis.DoesNotExist:
        ai_analysis = None

    data = {
        "stock": {
            "name": stock.name,
            "ticker": stock.ticker,
            "market": stock.market,
            "logo_url": stock.logo_url,
        },
        "price": {
            "current_price": float(price.current_price) if price else None,
            "currency": price.currency if price else None,
            "change_rate": float(price.change_rate) if price else None,
            "change_amount": float(price.change_amount) if price else None,
            "volume": price.volume if price else None,
            "updated_at": price.updated_at if price else None,
        },
        "chart": [
            {
                "time": point.time,
                "price": float(point.price),
                "volume": point.volume,
            }
            for point in chart_points
        ],
        "social": {
            "tweet_volume": trend_stat.tweet_volume if trend_stat else 0,
            "one_hour_change_rate": float(trend_stat.one_hour_change_rate) if trend_stat else 0,
            "hot_tweets": [
                {
                    "author_name": tweet.author_name,
                    "author_handle": tweet.author_handle,
                    "content": tweet.content,
                    "hashtags": tweet.hashtags,
                    "sentiment": tweet.sentiment,
                    "like_count": tweet.like_count,
                    "reply_count": tweet.reply_count,
                    "repost_count": tweet.repost_count,
                    "is_hot": tweet.is_hot,
                    "posted_at": tweet.posted_at,
                }
                for tweet in tweets
            ],
        },
        "ai_analysis": StockAiAnalysisSerializer(ai_analysis).data if ai_analysis else None,
    }

    return Response({
        "success": True,
        "message": "종목 통합 정보를 조회했습니다.",
        "data": data,
    })