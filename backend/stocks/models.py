from django.conf import settings
from django.db import models


class Stock(models.Model):
    name = models.CharField(max_length=100)
    ticker = models.CharField(max_length=20, unique=True)
    market = models.CharField(max_length=50, blank=True, null=True)
    logo_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.ticker})"


class StockPrice(models.Model):
    stock = models.OneToOneField(
        Stock,
        on_delete=models.CASCADE,
        related_name="price"
    )
    current_price = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=10, default="USD")
    change_rate = models.DecimalField(max_digits=6, decimal_places=2)
    change_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    volume = models.BigIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.stock.ticker} - {self.current_price}"


class StockChartPoint(models.Model):
    stock = models.ForeignKey(
        Stock,
        on_delete=models.CASCADE,
        related_name="chart_points"
    )
    time = models.DateTimeField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    volume = models.BigIntegerField(default=0)

    class Meta:
        ordering = ["time"]

    def __str__(self):
        return f"{self.stock.ticker} - {self.time} - {self.price}"


class Watchlist(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="watchlists"
    )
    stock = models.ForeignKey(
        Stock,
        on_delete=models.CASCADE,
        related_name="watchlisted_by"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "stock")

    def __str__(self):
        return f"{self.user} - {self.stock.ticker}"