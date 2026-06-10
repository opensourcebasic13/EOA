from django.core.management.base import BaseCommand

from analysis.processor import EOSAIProcessor
from stocks.models import Stock, StockAiAnalysis
from tweets.models import TweetPost


class Command(BaseCommand):
    help = "저장된 트윗 데이터를 mT5와 FinBERT로 분석하여 AI 분석 결과를 저장합니다."

    def add_arguments(self, parser):
        parser.add_argument(
            "--ticker",
            type=str,
            default="TSLA",
            help="분석할 주식 티커입니다. 기본값은 TSLA입니다.",
        )

        parser.add_argument(
            "--all",
            action="store_true",
            help="DB에 있는 모든 종목을 분석합니다.",
        )

    def handle(self, *args, **options):
        processor = EOSAIProcessor()

        if options["all"]:
            stocks = Stock.objects.all()
        else:
            stocks = Stock.objects.filter(ticker__iexact=options["ticker"])

        for stock in stocks:
            self.analyze_stock(processor, stock)

    def analyze_stock(self, processor, stock):
        tweets = TweetPost.objects.filter(stock=stock).order_by(
            "-is_hot",
            "-like_count",
            "-repost_count",
            "-posted_at"
        )[:20]

        if not tweets:
            self.stdout.write(self.style.WARNING(
                f"{stock.ticker} 분석할 트윗 데이터가 없습니다."
            ))
            return

        text = "\n".join([tweet.content for tweet in tweets])

        result = processor.process(text, ticker=stock.ticker)

        if "error" in result:
            self.stdout.write(self.style.WARNING(
                f"{stock.ticker} AI 분석 실패: {result['error']}"
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
            f"{stock.ticker} AI 분석 결과 저장 완료: {result.get('main_sentiment')}"
        ))