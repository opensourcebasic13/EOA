from rest_framework import serializers
from .models import Stock, StockChartPoint, StockTrendStat, StockAiAnalysis


class StockSummarySerializer(serializers.ModelSerializer):
    current_price = serializers.SerializerMethodField()
    currency = serializers.SerializerMethodField()
    price_change_rate = serializers.SerializerMethodField()
    price_change_amount = serializers.SerializerMethodField()
    volume = serializers.SerializerMethodField()

    class Meta:
        model = Stock
        fields = [
            "name",
            "ticker",
            "market",
            "logo_url",
            "current_price",
            "currency",
            "price_change_rate",
            "price_change_amount",
            "volume",
        ]

    def get_price_obj(self, obj):
        try:
            return obj.price
        except Exception:
            return None

    def get_current_price(self, obj):
        price = self.get_price_obj(obj)
        return float(price.current_price) if price else None

    def get_currency(self, obj):
        price = self.get_price_obj(obj)
        return price.currency if price else None

    def get_price_change_rate(self, obj):
        price = self.get_price_obj(obj)
        return float(price.change_rate) if price else None

    def get_price_change_amount(self, obj):
        price = self.get_price_obj(obj)
        return float(price.change_amount) if price else None

    def get_volume(self, obj):
        price = self.get_price_obj(obj)
        return price.volume if price else None


class StockDetailSerializer(StockSummarySerializer):
    updated_at = serializers.SerializerMethodField()

    class Meta(StockSummarySerializer.Meta):
        fields = StockSummarySerializer.Meta.fields + [
            "updated_at",
        ]

    def get_updated_at(self, obj):
        price = self.get_price_obj(obj)
        return price.updated_at if price else None


class StockTrendStatSerializer(serializers.ModelSerializer):
    rank = serializers.SerializerMethodField()

    name = serializers.CharField(source="stock.name")
    ticker = serializers.CharField(source="stock.ticker")
    market = serializers.CharField(source="stock.market")
    logo_url = serializers.URLField(source="stock.logo_url", allow_null=True)

    current_price = serializers.SerializerMethodField()
    currency = serializers.SerializerMethodField()
    price_change_rate = serializers.SerializerMethodField()
    price_change_amount = serializers.SerializerMethodField()

    class Meta:
        model = StockTrendStat
        fields = [
            "rank",
            "name",
            "ticker",
            "market",
            "logo_url",
            "tweet_volume",
            "one_hour_change_rate",
            "current_price",
            "currency",
            "price_change_rate",
            "price_change_amount",
            "updated_at",
        ]

    def get_rank(self, obj):
        rank_map = self.context.get("rank_map", {})
        return rank_map.get(obj.id)

    def get_price_obj(self, obj):
        try:
            return obj.stock.price
        except Exception:
            return None

    def get_current_price(self, obj):
        price = self.get_price_obj(obj)
        return float(price.current_price) if price else None

    def get_currency(self, obj):
        price = self.get_price_obj(obj)
        return price.currency if price else None

    def get_price_change_rate(self, obj):
        price = self.get_price_obj(obj)
        return float(price.change_rate) if price else None

    def get_price_change_amount(self, obj):
        price = self.get_price_obj(obj)
        return float(price.change_amount) if price else None


class StockChartPointSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField()

    class Meta:
        model = StockChartPoint
        fields = [
            "time",
            "price",
            "volume",
        ]

    def get_price(self, obj):
        return float(obj.price)

class StockAiAnalysisSerializer(serializers.ModelSerializer):
    ticker = serializers.CharField(source="stock.ticker", read_only=True)
    stock_name = serializers.CharField(source="stock.name", read_only=True)
    sentiment_scores = serializers.SerializerMethodField()
    model_info = serializers.SerializerMethodField()

    class Meta:
        model = StockAiAnalysis
        fields = [
            "ticker",
            "stock_name",
            "summary",
            "summary_ko",
            "main_sentiment",
            "sentiment_scores",
            "keywords",
            "model_info",
            "analyzed_at",
        ]

    def get_sentiment_scores(self, obj):
        return {
            "positive": float(obj.positive_score),
            "negative": float(obj.negative_score),
            "neutral": float(obj.neutral_score),
        }

    def get_model_info(self, obj):
        return {
            "summary_model": obj.summary_model,
            "sentiment_model": obj.sentiment_model,
        }