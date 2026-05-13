from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response

from stocks.models import Stock
from .models import TweetPost
from .serializers import TweetPostSerializer


@api_view(["GET"])
def hot_tweets(request, ticker):
    stock = get_object_or_404(Stock, ticker__iexact=ticker)

    tweets = TweetPost.objects.filter(stock=stock).order_by(
        "-is_hot",
        "-like_count",
        "-repost_count",
        "-posted_at"
    )[:10]

    serializer = TweetPostSerializer(tweets, many=True)

    return Response(serializer.data)