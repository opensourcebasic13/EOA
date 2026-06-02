from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from stocks.models import Stock, StockPrice, StockChartPoint, StockTrendStat, StockAiAnalysis
from tweets.models import TweetPost


class Command(BaseCommand):
    help = "EOA 샘플 데이터 생성"

    def handle(self, *args, **options):
        now = timezone.now()

        stocks_data = [
            {"name": "Tesla", "ticker": "TSLA", "market": "NASDAQ", "price": 181.06, "change_rate": 2.57, "change_amount": 4.53, "volume": 12534000, "tweet_volume": 24851, "one_hour_change_rate": 23.4, "keywords": ["robotaxi", "FSD", "delivery", "valuation", "earnings"]},
            {"name": "Ford", "ticker": "F", "market": "NYSE", "price": 12.45, "change_rate": -1.82, "change_amount": -0.23, "volume": 8100000, "tweet_volume": 9200, "one_hour_change_rate": -8.4, "keywords": ["EV", "F-150", "Lightning", "recall", "sales"]},
            {"name": "NVIDIA", "ticker": "NVDA", "market": "NASDAQ", "price": 1037.89, "change_rate": -1.12, "change_amount": -11.72, "volume": 8932000, "tweet_volume": 18932, "one_hour_change_rate": -12.8, "keywords": ["AI chip", "GPU", "data center", "earnings", "Blackwell"]},
            {"name": "Apple", "ticker": "AAPL", "market": "NASDAQ", "price": 192.58, "change_rate": -0.53, "change_amount": -1.02, "volume": 5320000, "tweet_volume": 8245, "one_hour_change_rate": -5.2, "keywords": ["iPhone", "AI", "services", "China", "WWDC"]},
            {"name": "Microsoft", "ticker": "MSFT", "market": "NASDAQ", "price": 421.44, "change_rate": 1.04, "change_amount": 4.33, "volume": 6120000, "tweet_volume": 15620, "one_hour_change_rate": 18.1, "keywords": ["Azure", "OpenAI", "Copilot", "cloud", "AI"]},
            {"name": "Amazon", "ticker": "AMZN", "market": "NASDAQ", "price": 184.72, "change_rate": 0.82, "change_amount": 1.50, "volume": 4920000, "tweet_volume": 10120, "one_hour_change_rate": 9.7, "keywords": ["AWS", "retail", "advertising", "cloud", "earnings"]},
            {"name": "Alphabet", "ticker": "GOOGL", "market": "NASDAQ", "price": 176.24, "change_rate": 1.31, "change_amount": 2.28, "volume": 4210000, "tweet_volume": 11205, "one_hour_change_rate": 13.2, "keywords": ["Google", "Gemini", "AI", "search", "ads"]},
            {"name": "Meta", "ticker": "META", "market": "NASDAQ", "price": 487.36, "change_rate": 2.04, "change_amount": 9.74, "volume": 3810000, "tweet_volume": 12670, "one_hour_change_rate": 21.5, "keywords": ["AI", "Instagram", "Reels", "ads", "metaverse"]},
            {"name": "AMD", "ticker": "AMD", "market": "NASDAQ", "price": 167.18, "change_rate": 1.35, "change_amount": 2.23, "volume": 7230000, "tweet_volume": 9842, "one_hour_change_rate": 15.7, "keywords": ["AI chip", "GPU", "MI300", "data center", "semiconductor"]},
            {"name": "Palantir", "ticker": "PLTR", "market": "NYSE", "price": 23.48, "change_rate": 4.18, "change_amount": 0.94, "volume": 6320000, "tweet_volume": 12309, "one_hour_change_rate": 45.6, "keywords": ["AI platform", "government", "commercial", "AIP", "growth"]},
            {"name": "Netflix", "ticker": "NFLX", "market": "NASDAQ", "price": 642.18, "change_rate": -0.74, "change_amount": -4.78, "volume": 2910000, "tweet_volume": 7320, "one_hour_change_rate": -3.1, "keywords": ["subscriber", "content", "streaming", "ads", "earnings"]},
        ]

        for item in stocks_data:
            stock, _ = Stock.objects.update_or_create(
                ticker=item["ticker"],
                defaults={"name": item["name"], "market": item["market"]},
            )
            StockPrice.objects.update_or_create(
                stock=stock,
                defaults={"current_price": item["price"], "currency": "USD", "change_rate": item["change_rate"], "change_amount": item["change_amount"], "volume": item["volume"]},
            )
            StockTrendStat.objects.update_or_create(
                stock=stock,
                defaults={"tweet_volume": item["tweet_volume"], "one_hour_change_rate": item["one_hour_change_rate"]},
            )
            StockAiAnalysis.objects.update_or_create(
                stock=stock,
                defaults={
                    "summary": f"{item['name']} is being discussed around {', '.join(item['keywords'][:3])}. Investors are reacting to recent market expectations.",
                    "summary_ko": f"{item['name']}의 {', '.join(item['keywords'][:3])} 관련 투자 심리가 주목받고 있습니다.",
                    "main_sentiment": "positive" if item["change_rate"] >= 0 else "negative",
                    "positive_score": 60.0 if item["change_rate"] >= 0 else 28.0,
                    "negative_score": 22.0 if item["change_rate"] >= 0 else 52.0,
                    "neutral_score": 18.0 if item["change_rate"] >= 0 else 20.0,
                    "keywords": item["keywords"],
                    "summary_model": "mT5",
                    "sentiment_model": "FinBERT",
                },
            )

        self.create_tweets(now)
        self.stdout.write(self.style.SUCCESS("EOA 샘플 데이터 생성 완료"))

    def create_tweets(self, now):
        tsla = Stock.objects.get(ticker="TSLA")
        ford = Stock.objects.get(ticker="F")

        TweetPost.objects.filter(stock__ticker__in=["TSLA", "F"]).delete()

        # TSLA 차트 데이터
        for stock in [tsla, ford]:
            StockChartPoint.objects.filter(stock=stock).delete()
            base_price = float(stock.price.current_price)
            for i, ratio in enumerate([0.96, 0.98, 0.99, 1.01, 1.02, 1.0]):
                StockChartPoint.objects.create(
                    stock=stock,
                    time=now - timedelta(hours=6 - i),
                    price=round(base_price * ratio, 2),
                    volume=1000000 + i * 120000,
                )

        # ===== TSLA/F 경쟁사 트윗 10개 =====
        competitor_tweets = [
            # TSLA 호재 → F 악재
            {"stock": tsla, "author_name": "EV Bull", "author_handle": "@ev_bull", "content": "Tesla just crushed Q2 earnings! Delivery numbers smashed expectations. $TSLA is the clear EV leader.", "hashtags": ["TSLA", "EV", "earnings"], "sentiment": "positive", "like_count": 892, "reply_count": 67, "repost_count": 234, "is_hot": True, "minutes_ago": 10},
            {"stock": ford, "author_name": "Auto Analyst", "author_handle": "@auto_analyst", "content": "Tesla's Q2 surge is a red flag for legacy automakers. Ford's EV transition looks shaky by comparison. $F under pressure.", "hashtags": ["F", "TSLA", "EV"], "sentiment": "negative", "like_count": 541, "reply_count": 89, "repost_count": 102, "is_hot": True, "minutes_ago": 15},
            {"stock": tsla, "author_name": "Tech Investor", "author_handle": "@tech_inv", "content": "Tesla FSD v13 is miles ahead of any competitor. Ford's BlueCruise can't touch it. Long $TSLA.", "hashtags": ["TSLA", "FSD", "autonomy"], "sentiment": "positive", "like_count": 703, "reply_count": 44, "repost_count": 187, "is_hot": True, "minutes_ago": 25},
            {"stock": ford, "author_name": "Market Bear", "author_handle": "@market_bear", "content": "Ford cut EV production targets again while Tesla expands Gigafactories. The gap is widening. Bearish on $F.", "hashtags": ["F", "EV", "bearish"], "sentiment": "negative", "like_count": 412, "reply_count": 78, "repost_count": 95, "is_hot": False, "minutes_ago": 30},
            {"stock": tsla, "author_name": "Retail Trader", "author_handle": "@retail_tr", "content": "Bought more $TSLA on the dip. Tesla's energy business alone is worth more than Ford's entire market cap.", "hashtags": ["TSLA", "buyThedip", "energy"], "sentiment": "positive", "like_count": 628, "reply_count": 55, "repost_count": 143, "is_hot": True, "minutes_ago": 40},
            {"stock": ford, "author_name": "Value Hunter", "author_handle": "@value_hunter", "content": "$F dividend still looks attractive but Tesla's momentum is stealing institutional money from legacy auto.", "hashtags": ["F", "dividend", "TSLA"], "sentiment": "negative", "like_count": 289, "reply_count": 41, "repost_count": 67, "is_hot": False, "minutes_ago": 50},
            {"stock": tsla, "author_name": "Quant Fund", "author_handle": "@quant_fund", "content": "Tesla volume spike detected. Options flow heavily bullish. Price target raised to $250. $TSLA", "hashtags": ["TSLA", "options", "bullish"], "sentiment": "positive", "like_count": 774, "reply_count": 92, "repost_count": 198, "is_hot": True, "minutes_ago": 60},
            {"stock": ford, "author_name": "Sector Watch", "author_handle": "@sector_watch", "content": "EV sector rotation happening now. Money flowing from $F to $TSLA as Tesla dominates the narrative.", "hashtags": ["F", "TSLA", "rotation"], "sentiment": "negative", "like_count": 356, "reply_count": 48, "repost_count": 88, "is_hot": False, "minutes_ago": 70},
            {"stock": tsla, "author_name": "Growth Scout", "author_handle": "@growth_scout", "content": "Tesla Cybertruck production ramping faster than expected. Demand backlog still strong. $TSLA breakout incoming.", "hashtags": ["TSLA", "Cybertruck", "growth"], "sentiment": "positive", "like_count": 519, "reply_count": 37, "repost_count": 121, "is_hot": False, "minutes_ago": 80},
            {"stock": ford, "author_name": "Risk Desk", "author_handle": "@risk_desk", "content": "Ford recall costs mounting. Combined with EV losses, $F free cash flow under serious pressure this quarter.", "hashtags": ["F", "recall", "risk"], "sentiment": "negative", "like_count": 445, "reply_count": 63, "repost_count": 109, "is_hot": True, "minutes_ago": 90},
        ]

        for t in competitor_tweets:
            TweetPost.objects.create(
                stock=t["stock"],
                author_name=t["author_name"],
                author_handle=t["author_handle"],
                content=t["content"],
                hashtags=t["hashtags"],
                sentiment=t["sentiment"],
                like_count=t["like_count"],
                reply_count=t["reply_count"],
                repost_count=t["repost_count"],
                is_hot=t["is_hot"],
                posted_at=now - timedelta(minutes=t["minutes_ago"]),
            )

        # ===== 일반 트윗 10개 (TSLA 5개, F 5개) =====
        general_tweets = [
            {"stock": tsla, "author_name": "Daily Trader", "author_handle": "@daily_trader", "content": "Watching $TSLA closely today. Chart looking interesting around this level.", "hashtags": ["TSLA", "chart"], "sentiment": "neutral", "like_count": 123, "reply_count": 12, "repost_count": 28, "is_hot": False, "minutes_ago": 100},
            {"stock": tsla, "author_name": "News Flash", "author_handle": "@news_flash", "content": "Tesla opens new service center in Austin. Expanding domestic support infrastructure. $TSLA", "hashtags": ["TSLA", "Austin"], "sentiment": "neutral", "like_count": 98, "reply_count": 8, "repost_count": 21, "is_hot": False, "minutes_ago": 110},
            {"stock": tsla, "author_name": "Long Term", "author_handle": "@long_term", "content": "Not selling my $TSLA. Five year horizon. Autonomous driving will reshape everything.", "hashtags": ["TSLA", "longterm"], "sentiment": "positive", "like_count": 201, "reply_count": 18, "repost_count": 47, "is_hot": False, "minutes_ago": 120},
            {"stock": tsla, "author_name": "Skeptic Joe", "author_handle": "@skeptic_joe", "content": "Tesla valuation still seems stretched at these levels. PE ratio hard to justify. $TSLA", "hashtags": ["TSLA", "valuation"], "sentiment": "negative", "like_count": 167, "reply_count": 34, "repost_count": 39, "is_hot": False, "minutes_ago": 130},
            {"stock": tsla, "author_name": "Weekend Trader", "author_handle": "@weekend_tr", "content": "Added small position in $TSLA ahead of earnings. Let's see what happens.", "hashtags": ["TSLA", "earnings"], "sentiment": "neutral", "like_count": 88, "reply_count": 6, "repost_count": 14, "is_hot": False, "minutes_ago": 140},
            {"stock": ford, "author_name": "Blue Collar", "author_handle": "@blue_collar", "content": "Ford still sells more trucks than anyone in America. Don't count out $F yet.", "hashtags": ["F", "Ford", "trucks"], "sentiment": "positive", "like_count": 312, "reply_count": 29, "repost_count": 74, "is_hot": False, "minutes_ago": 150},
            {"stock": ford, "author_name": "Dividend Fan", "author_handle": "@dividend_fan", "content": "$F dividend yield looks solid for income investors. Not a growth play but steady.", "hashtags": ["F", "dividend"], "sentiment": "positive", "like_count": 178, "reply_count": 14, "repost_count": 38, "is_hot": False, "minutes_ago": 160},
            {"stock": ford, "author_name": "Auto Watch", "author_handle": "@auto_watch", "content": "Ford Pro commercial vehicle unit is actually performing well. Hidden gem within $F.", "hashtags": ["F", "FordPro"], "sentiment": "positive", "like_count": 245, "reply_count": 19, "repost_count": 56, "is_hot": False, "minutes_ago": 170},
            {"stock": ford, "author_name": "Short Seller", "author_handle": "@short_sell", "content": "Increased my short position on $F. EV losses are unsustainable at this rate.", "hashtags": ["F", "short", "EV"], "sentiment": "negative", "like_count": 198, "reply_count": 41, "repost_count": 45, "is_hot": False, "minutes_ago": 180},
            {"stock": ford, "author_name": "Neutral Ned", "author_handle": "@neutral_ned", "content": "Ford Q3 guidance will be key. Watching $F for any surprise. Neither bullish nor bearish right now.", "hashtags": ["F", "guidance"], "sentiment": "neutral", "like_count": 134, "reply_count": 11, "repost_count": 27, "is_hot": False, "minutes_ago": 190},
        ]

        for t in general_tweets:
            TweetPost.objects.create(
                stock=t["stock"],
                author_name=t["author_name"],
                author_handle=t["author_handle"],
                content=t["content"],
                hashtags=t["hashtags"],
                sentiment=t["sentiment"],
                like_count=t["like_count"],
                reply_count=t["reply_count"],
                repost_count=t["repost_count"],
                is_hot=t["is_hot"],
                posted_at=now - timedelta(minutes=t["minutes_ago"]),
            )