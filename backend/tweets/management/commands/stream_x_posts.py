from django.core.management.base import BaseCommand
from django.db.models import F
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from analysis.processor import EOSAIProcessor
from stocks.models import Stock, StockTrendStat, StockAiAnalysis
from tweets.models import TweetPost
from tweets.services.x_stream_client import (
    connect_stream,
    extract_ticker_from_payload,
    extract_author_info,
    get_stream_rules,
)


class Command(BaseCommand):
    help = "X API filtered stream으로 이미 등록된 rule에 맞는 게시글을 수집합니다."

    def add_arguments(self, parser):
        parser.add_argument(
            "--max-count",
            type=int,
            default=0,
            help="테스트용 최대 수집 개수입니다. 0이면 계속 실행합니다.",
        )

        parser.add_argument(
            "--show-rules",
            action="store_true",
            help="현재 X Developer에 등록된 stream rule을 출력합니다.",
        )

        parser.add_argument(
            "--auto-ai",
            action="store_true",
            help="새 트윗 저장 후 AI 분석 결과를 자동 업데이트합니다.",
        )

        parser.add_argument(
            "--ai-every",
            type=int,
            default=1,
            help="몇 개의 새 트윗마다 AI를 업데이트할지 설정합니다. 기본값은 1입니다.",
        )

    def handle(self, *args, **options):
        if options["show_rules"]:
            rules = get_stream_rules()
            self.stdout.write(self.style.SUCCESS("현재 등록된 X stream rules:"))
            self.stdout.write(str(rules))
            return

        max_count = options["max_count"]
        auto_ai = options["auto_ai"]
        ai_every = options["ai_every"]

        count = 0
        ai_count_by_ticker = {}

        processor = None

        if auto_ai:
            self.stdout.write(self.style.WARNING("AI 자동 업데이트 모드가 켜졌습니다."))
            self.stdout.write(self.style.WARNING("처음 실행 시 모델 로딩 때문에 시간이 걸릴 수 있습니다."))
            processor = EOSAIProcessor()

        self.stdout.write(self.style.SUCCESS("X stream 수집 시작"))
        self.stdout.write(self.style.WARNING("이미 등록된 X Developer rule을 사용합니다. 새 rule은 등록하지 않습니다."))

        for payload in connect_stream():
            saved_ticker = self.save_payload(payload)

            if saved_ticker:
                count += 1

                if auto_ai:
                    ai_count_by_ticker[saved_ticker] = ai_count_by_ticker.get(saved_ticker, 0) + 1

                    if ai_count_by_ticker[saved_ticker] >= ai_every:
                        try:
                            self.update_ai_analysis(processor, saved_ticker)
                            ai_count_by_ticker[saved_ticker] = 0
                        except Exception as error:
                            self.stdout.write(self.style.WARNING(
                                f"{saved_ticker} AI 자동 업데이트 실패: {error}"
                            ))

            if max_count and count >= max_count:
                self.stdout.write(self.style.SUCCESS("테스트 수집 완료"))
                break

    def save_payload(self, payload):
        tweet_data = payload.get("data", {})

        if not tweet_data:
            return None

        ticker = extract_ticker_from_payload(payload)

        if not ticker:
            self.stdout.write(self.style.WARNING("종목을 식별하지 못한 트윗입니다."))
            return None

        try:
            stock = Stock.objects.get(ticker=ticker)
        except Stock.DoesNotExist:
            self.stdout.write(self.style.WARNING(f"{ticker} 종목이 DB에 없습니다."))
            return None

        author_info = extract_author_info(payload)
        public_metrics = tweet_data.get("public_metrics", {})

        posted_at = parse_datetime(tweet_data.get("created_at", ""))

        if posted_at is None:
            posted_at = timezone.now()

        TweetPost.objects.create(
            stock=stock,
            author_name=author_info["author_name"],
            author_handle=author_info["author_handle"],
            content=tweet_data.get("text", ""),
            hashtags=[ticker, stock.name],
            sentiment="neutral",
            like_count=public_metrics.get("like_count", 0),
            reply_count=public_metrics.get("reply_count", 0),
            repost_count=public_metrics.get("retweet_count", 0),
            is_hot=True,
            posted_at=posted_at,
        )

        trend_stat, _ = StockTrendStat.objects.get_or_create(
            stock=stock,
            defaults={
                "tweet_volume": 0,
                "one_hour_change_rate": 0,
            },
        )

        StockTrendStat.objects.filter(id=trend_stat.id).update(
            tweet_volume=F("tweet_volume") + 1
        )

        self.stdout.write(self.style.SUCCESS(
            f"{ticker} 실제 X stream 게시글 저장 완료"
        ))

        return ticker

    def update_ai_analysis(self, processor, ticker):
        stock = Stock.objects.get(ticker=ticker)

        tweets = TweetPost.objects.filter(stock=stock).order_by(
            "-is_hot",
            "-like_count",
            "-repost_count",
            "-posted_at"
        )[:20]

        if not tweets:
            self.stdout.write(self.style.WARNING(
                f"{ticker} AI 분석할 트윗 데이터가 없습니다."
            ))
            return

        text = "\n".join([tweet.content for tweet in tweets])

        result = processor.process(text, ticker=ticker)

        if "error" in result:
            self.stdout.write(self.style.WARNING(
                f"{ticker} AI 분석 실패: {result['error']}"
            ))
            return

        sentiment_scores = result.get("sentiment_scores", {})
        model_info = result.get("model_info", {})

        StockAiAnalysis.objects.update_or_create(
            stock=stock,
            defaults={
                "summary": result.get("summary", ""),
                "summary_ko": result.get("summary_ko", ""),
                "main_sentiment": result.get("main_sentiment", "neutral"),
                "positive_score": sentiment_scores.get("positive", 0),
                "negative_score": sentiment_scores.get("negative", 0),
                "neutral_score": sentiment_scores.get("neutral", 0),
                "keywords": result.get("keywords", []),
                "summary_model": model_info.get("summary_model", "mT5"),
                "sentiment_model": model_info.get("sentiment_model", "FinBERT"),
            }
        )

        self.stdout.write(self.style.SUCCESS(
            f"{ticker} AI 분석 자동 업데이트 완료: {result.get('main_sentiment')}"
        ))