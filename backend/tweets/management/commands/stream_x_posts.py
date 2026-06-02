from requests.exceptions import HTTPError

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from stocks.models import Stock, StockTrendStat
from tweets.models import TweetPost
from tweets.services.x_stream_client import (
    SUPPORTED_STOCKS,
    fetch_recent_posts,
    build_sample_posts,
)


class Command(BaseCommand):
    help = "X API recent search로 해외주식 관련 최근 게시글을 수집합니다."

    def add_arguments(self, parser):
        parser.add_argument(
            "--max-count",
            type=int,
            default=10,
            help="종목별 가져올 게시글 수입니다.",
        )

        parser.add_argument(
            "--sample",
            action="store_true",
            help="X API를 호출하지 않고 샘플 게시글을 저장합니다.",
        )

    def handle(self, *args, **options):
        max_count = options["max_count"]
        use_sample = options["sample"]

        for item in SUPPORTED_STOCKS:
            ticker = item["ticker"]
            name = item["name"]

            self.stdout.write(f"{ticker} X recent search 수집 시작")

            try:
                stock = Stock.objects.get(ticker=ticker)
            except Stock.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"{ticker} 종목이 DB에 없습니다."))
                continue

            if use_sample:
                posts = build_sample_posts(ticker, name)
            else:
                try:
                    posts = fetch_recent_posts(ticker, name, max_results=max_count)
                except HTTPError as error:
                    status_code = error.response.status_code if error.response else None

                    if status_code == 402:
                        self.stdout.write(self.style.WARNING(
                            f"{ticker} X API 402 Payment Required: 현재 계정/크레딧에서 recent search가 제한되었습니다."
                        ))
                        self.stdout.write(self.style.WARNING(
                            f"{ticker} 발표/개발용 샘플 게시글을 대신 저장합니다."
                        ))
                        posts = build_sample_posts(ticker, name)
                    else:
                        self.stdout.write(self.style.WARNING(f"{ticker} X API 오류: {error}"))
                        continue
                except Exception as error:
                    self.stdout.write(self.style.WARNING(f"{ticker} X 수집 실패: {error}"))
                    posts = build_sample_posts(ticker, name)

            self.save_posts(stock, ticker, posts)

        self.stdout.write(self.style.SUCCESS("X 게시글 수집 작업 완료"))

    def save_posts(self, stock, ticker, posts):
        TweetPost.objects.filter(stock=stock).delete()

        for index, post in enumerate(posts):
            posted_at = None

            if post.get("posted_at"):
                posted_at = parse_datetime(post["posted_at"])

            if posted_at is None:
                posted_at = timezone.now()

            TweetPost.objects.create(
                stock=stock,
                author_name=post.get("author_name", "X User"),
                author_handle=post.get("author_handle", "@x_user"),
                content=post.get("content", ""),
                hashtags=[ticker, stock.name],
                sentiment="neutral",
                like_count=post.get("like_count", 0),
                reply_count=post.get("reply_count", 0),
                repost_count=post.get("repost_count", 0),
                is_hot=index < 3,
                posted_at=posted_at,
            )

        StockTrendStat.objects.update_or_create(
            stock=stock,
            defaults={
                "tweet_volume": len(posts),
                "one_hour_change_rate": 0,
            },
        )

        self.stdout.write(self.style.SUCCESS(
            f"{ticker} 게시글 {len(posts)}개 저장 완료"
        ))