from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from stocks.models import (
    Stock,
    StockPrice,
    StockChartPoint,
    StockTrendStat,
    StockAiAnalysis,
)
from tweets.models import TweetPost


class Command(BaseCommand):
    help = "EOA 개발용 해외주식 10개 샘플 데이터를 생성합니다."

    def handle(self, *args, **options):
        now = timezone.now()

        stocks_data = [
            {
                "name": "Tesla",
                "ticker": "TSLA",
                "market": "NASDAQ",
                "price": 181.06,
                "change_rate": 2.57,
                "change_amount": 4.53,
                "volume": 12534000,
                "tweet_volume": 24851,
                "one_hour_change_rate": 23.4,
                "keywords": ["robotaxi", "FSD", "delivery", "valuation", "earnings"],
            },
            {
                "name": "NVIDIA",
                "ticker": "NVDA",
                "market": "NASDAQ",
                "price": 1037.89,
                "change_rate": -1.12,
                "change_amount": -11.72,
                "volume": 8932000,
                "tweet_volume": 18932,
                "one_hour_change_rate": -12.8,
                "keywords": ["AI chip", "GPU", "data center", "earnings", "Blackwell"],
            },
            {
                "name": "Apple",
                "ticker": "AAPL",
                "market": "NASDAQ",
                "price": 192.58,
                "change_rate": -0.53,
                "change_amount": -1.02,
                "volume": 5320000,
                "tweet_volume": 8245,
                "one_hour_change_rate": -5.2,
                "keywords": ["iPhone", "AI", "services", "China", "WWDC"],
            },
            {
                "name": "Microsoft",
                "ticker": "MSFT",
                "market": "NASDAQ",
                "price": 421.44,
                "change_rate": 1.04,
                "change_amount": 4.33,
                "volume": 6120000,
                "tweet_volume": 15620,
                "one_hour_change_rate": 18.1,
                "keywords": ["Azure", "OpenAI", "Copilot", "cloud", "AI"],
            },
            {
                "name": "Amazon",
                "ticker": "AMZN",
                "market": "NASDAQ",
                "price": 184.72,
                "change_rate": 0.82,
                "change_amount": 1.50,
                "volume": 4920000,
                "tweet_volume": 10120,
                "one_hour_change_rate": 9.7,
                "keywords": ["AWS", "retail", "advertising", "cloud", "earnings"],
            },
            {
                "name": "Alphabet",
                "ticker": "GOOGL",
                "market": "NASDAQ",
                "price": 176.24,
                "change_rate": 1.31,
                "change_amount": 2.28,
                "volume": 4210000,
                "tweet_volume": 11205,
                "one_hour_change_rate": 13.2,
                "keywords": ["Google", "Gemini", "AI", "search", "ads"],
            },
            {
                "name": "Meta",
                "ticker": "META",
                "market": "NASDAQ",
                "price": 487.36,
                "change_rate": 2.04,
                "change_amount": 9.74,
                "volume": 3810000,
                "tweet_volume": 12670,
                "one_hour_change_rate": 21.5,
                "keywords": ["AI", "Instagram", "Reels", "ads", "metaverse"],
            },
            {
                "name": "AMD",
                "ticker": "AMD",
                "market": "NASDAQ",
                "price": 167.18,
                "change_rate": 1.35,
                "change_amount": 2.23,
                "volume": 7230000,
                "tweet_volume": 9842,
                "one_hour_change_rate": 15.7,
                "keywords": ["AI chip", "GPU", "MI300", "data center", "semiconductor"],
            },
            {
                "name": "Palantir",
                "ticker": "PLTR",
                "market": "NYSE",
                "price": 23.48,
                "change_rate": 4.18,
                "change_amount": 0.94,
                "volume": 6320000,
                "tweet_volume": 12309,
                "one_hour_change_rate": 45.6,
                "keywords": ["AI platform", "government", "commercial", "AIP", "growth"],
            },
            {
                "name": "Netflix",
                "ticker": "NFLX",
                "market": "NASDAQ",
                "price": 642.18,
                "change_rate": -0.74,
                "change_amount": -4.78,
                "volume": 2910000,
                "tweet_volume": 7320,
                "one_hour_change_rate": -3.1,
                "keywords": ["subscriber", "content", "streaming", "ads", "earnings"],
            },
        ]

        for item in stocks_data:
            stock, _ = Stock.objects.update_or_create(
                ticker=item["ticker"],
                defaults={
                    "name": item["name"],
                    "market": item["market"],
                },
            )

            StockPrice.objects.update_or_create(
                stock=stock,
                defaults={
                    "current_price": item["price"],
                    "currency": "USD",
                    "change_rate": item["change_rate"],
                    "change_amount": item["change_amount"],
                    "volume": item["volume"],
                },
            )

            StockTrendStat.objects.update_or_create(
                stock=stock,
                defaults={
                    "tweet_volume": item["tweet_volume"],
                    "one_hour_change_rate": item["one_hour_change_rate"],
                },
            )

            StockAiAnalysis.objects.update_or_create(
                stock=stock,
                defaults={
                    "summary": f"{item['name']} is being discussed around {', '.join(item['keywords'][:3])}. Investors are reacting to recent market expectations and sector momentum.",
                    "summary_ko": f"{item['name']}은(는) {', '.join(item['keywords'][:3])} 이슈를 중심으로 언급되고 있습니다. 투자자들은 최근 시장 기대감과 섹터 흐름에 반응하고 있습니다.",
                    "main_sentiment": "positive" if item["change_rate"] >= 0 else "negative",
                    "positive_score": 60.0 if item["change_rate"] >= 0 else 28.0,
                    "negative_score": 22.0 if item["change_rate"] >= 0 else 52.0,
                    "neutral_score": 18.0 if item["change_rate"] >= 0 else 20.0,
                    "keywords": item["keywords"],
                    "summary_model": "mT5",
                    "sentiment_model": "FinBERT",
                },
            )

        self.create_chart_and_tweets(now)

        self.stdout.write(self.style.SUCCESS("EOA 샘플 데이터 생성 완료"))

    def create_chart_and_tweets(self, now):
        target_tickers = ["TSLA", "NVDA"]

        for ticker in target_tickers:
            stock = Stock.objects.get(ticker=ticker)

            StockChartPoint.objects.filter(stock=stock).delete()
            TweetPost.objects.filter(stock=stock).delete()

            base_price = float(stock.price.current_price)
            chart_prices = [
                base_price * 0.96,
                base_price * 0.98,
                base_price * 0.99,
                base_price * 1.01,
                base_price * 1.02,
                base_price,
            ]

            for i, price in enumerate(chart_prices):
                StockChartPoint.objects.create(
                    stock=stock,
                    time=now - timedelta(hours=len(chart_prices) - i),
                    price=round(price, 2),
                    volume=1000000 + i * 120000,
                )

            tweets_data = [
                {
                    "author_name": "Market Watcher",
                    "author_handle": "@market_watcher",
                    "content": f"{stock.name} is gaining attention as investors discuss recent momentum and market expectations.",
                    "hashtags": [ticker, stock.name, "stocks"],
                    "sentiment": "positive",
                    "like_count": 512,
                    "reply_count": 34,
                    "repost_count": 128,
                    "is_hot": True,
                },
                {
                    "author_name": "AI Investor",
                    "author_handle": "@ai_investor",
                    "content": f"{ticker} is being mentioned frequently with AI and growth-related keywords today.",
                    "hashtags": [ticker, "AI", "growth"],
                    "sentiment": "positive",
                    "like_count": 401,
                    "reply_count": 28,
                    "repost_count": 96,
                    "is_hot": True,
                },
                {
                    "author_name": "Risk Monitor",
                    "author_handle": "@risk_monitor",
                    "content": f"Some traders remain cautious about {ticker} due to valuation and short-term volatility.",
                    "hashtags": [ticker, "risk", "valuation"],
                    "sentiment": "negative",
                    "like_count": 193,
                    "reply_count": 51,
                    "repost_count": 62,
                    "is_hot": False,
                },
                {
                    "author_name": "Chart Trader",
                    "author_handle": "@chart_trader",
                    "content": f"{ticker} is testing an important technical level. Traders are watching volume closely.",
                    "hashtags": [ticker, "chart", "trading"],
                    "sentiment": "neutral",
                    "like_count": 156,
                    "reply_count": 22,
                    "repost_count": 45,
                    "is_hot": False,
                },
            ]

            for i, item in enumerate(tweets_data):
                TweetPost.objects.create(
                    stock=stock,
                    author_name=item["author_name"],
                    author_handle=item["author_handle"],
                    content=item["content"],
                    hashtags=item["hashtags"],
                    sentiment=item["sentiment"],
                    like_count=item["like_count"],
                    reply_count=item["reply_count"],
                    repost_count=item["repost_count"],
                    is_hot=item["is_hot"],
                    posted_at=now - timedelta(minutes=20 + i * 15),
                )