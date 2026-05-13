from django.db import models
from stocks.models import Stock


class TweetPost(models.Model):
    SENTIMENT_CHOICES = [
        ("positive", "긍정"),
        ("negative", "부정"),
        ("neutral", "중립"),
    ]

    stock = models.ForeignKey(
        Stock,
        on_delete=models.CASCADE,
        related_name="tweets"
    )

    author_name = models.CharField(max_length=100)
    author_handle = models.CharField(max_length=100)
    content = models.TextField()

    hashtags = models.JSONField(default=list, blank=True)

    sentiment = models.CharField(
        max_length=20,
        choices=SENTIMENT_CHOICES,
        default="neutral"
    )

    like_count = models.IntegerField(default=0)
    reply_count = models.IntegerField(default=0)
    repost_count = models.IntegerField(default=0)

    is_hot = models.BooleanField(default=False)

    posted_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-like_count", "-repost_count", "-posted_at"]

    def __str__(self):
        return f"{self.stock.ticker} - {self.author_handle}"