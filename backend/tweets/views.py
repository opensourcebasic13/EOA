from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response

from stocks.models import Stock
from .models import TweetPost


@api_view(["GET"])
def hot_tweets(request, ticker):
    stock = get_object_or_404(Stock, ticker__iexact=ticker)

    tweets = TweetPost.objects.filter(stock=stock).order_by(
        "-is_hot",
        "-like_count",
        "-repost_count",
        "-posted_at"
    )[:10]

    data = [
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
    ]

    return Response(data)
