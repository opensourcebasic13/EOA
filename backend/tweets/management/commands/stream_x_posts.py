from django.core.management.base import BaseCommand
from django.db.models import F
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from stocks.models import Stock, StockTrendStat
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

    def handle(self, *args, **options):
        if options["show_rules"]:
            rules = get_stream_rules()
            self.stdout.write(self.style.SUCCESS("현재 등록된 X stream rules:"))
            self.stdout.write(str(rules))
            return

        max_count = options["max_count"]
        count = 0

        self.stdout.write(self.style.SUCCESS("X stream 수집 시작"))
        self.stdout.write(self.style.WARNING("이미 등록된 X Developer rule을 사용합니다. 새 rule은 등록하지 않습니다."))

        for payload in connect_stream():
            saved = self.save_payload(payload)

            if saved:
                count += 1

            if max_count and count >= max_count:
                self.stdout.write(self.style.SUCCESS("테스트 수집 완료"))
                break

    def save_payload(self, payload):
        tweet_data = payload.get("data", {})

        if not tweet_data:
            return False

        ticker = extract_ticker_from_payload(payload)

        if not ticker:
            self.stdout.write(self.style.WARNING("종목을 식별하지 못한 트윗입니다."))
            return False

        try:
            stock = Stock.objects.get(ticker=ticker)
        except Stock.DoesNotExist:
            self.stdout.write(self.style.WARNING(f"{ticker} 종목이 DB에 없습니다."))
            return False

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

        return True