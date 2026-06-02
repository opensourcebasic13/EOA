from rest_framework import serializers
from .models import TweetPost


class TweetPostSerializer(serializers.ModelSerializer):
    sentiment_label = serializers.CharField(source="get_sentiment_display")

    class Meta:
        model = TweetPost
        fields = [
            "author_name",
            "author_handle",
            "content",
            "hashtags",
            "sentiment",
            "sentiment_label",
            "like_count",
            "reply_count",
            "repost_count",
            "is_hot",
            "posted_at",
        ]
