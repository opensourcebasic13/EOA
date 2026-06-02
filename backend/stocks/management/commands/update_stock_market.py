import time

from django.core.management.base import BaseCommand

from stocks.models import Stock, StockPrice, StockChartPoint
from stocks.services.market_data import fetch_stock_quote, fetch_stock_chart


SUPPORTED_STOCKS = [
    {"ticker": "TSLA", "name": "Tesla", "market": "NASDAQ"},
    {"ticker": "NVDA", "name": "NVIDIA", "market": "NASDAQ"},
    {"ticker": "AAPL", "name": "Apple", "market": "NASDAQ"},
    {"ticker": "MSFT", "name": "Microsoft", "market": "NASDAQ"},
    {"ticker": "AMZN", "name": "Amazon", "market": "NASDAQ"},
    {"ticker": "GOOGL", "name": "Alphabet", "market": "NASDAQ"},
    {"ticker": "META", "name": "Meta", "market": "NASDAQ"},
    {"ticker": "AMD", "name": "AMD", "market": "NASDAQ"},
    {"ticker": "PLTR", "name": "Palantir", "market": "NYSE"},
    {"ticker": "NFLX", "name": "Netflix", "market": "NASDAQ"},
]


class Command(BaseCommand):
    help = "yfinance를 사용해 해외주식 10개의 현재가와 차트 데이터를 갱신합니다."

    def add_arguments(self, parser):
        parser.add_argument(
            "--loop",
            action="store_true",
            help="로컬 실행 중 일정 간격으로 주식 데이터를 자동 갱신합니다.",
        )

        parser.add_argument(
            "--interval",
            type=int,
            default=10,
            help="자동 갱신 간격입니다. 단위는 분입니다. 기본값은 10분입니다.",
        )

    def handle(self, *args, **options):
        loop = options["loop"]
        interval_minutes = options["interval"]

        if loop:
            self.stdout.write(self.style.SUCCESS(
                f"주식 데이터 자동 갱신 시작: {interval_minutes}분마다 갱신"
            ))

            try:
                while True:
                    self.update_all_stocks()
                    self.stdout.write(self.style.SUCCESS(
                        f"{interval_minutes}분 후 다시 갱신합니다."
                    ))
                    time.sleep(interval_minutes * 60)

            except KeyboardInterrupt:
                self.stdout.write(self.style.WARNING("주식 데이터 자동 갱신을 종료합니다."))
                return

        self.update_all_stocks()

    def update_all_stocks(self):
        for item in SUPPORTED_STOCKS:
            ticker = item["ticker"]

            self.stdout.write(f"{ticker} 주식 데이터 갱신 시작")

            stock, _ = Stock.objects.update_or_create(
                ticker=ticker,
                defaults={
                    "name": item["name"],
                    "market": item["market"],
                },
            )

            self.update_price(stock, ticker)
            self.update_chart(stock, ticker)

            self.stdout.write(self.style.SUCCESS(f"{ticker} 주식 데이터 갱신 완료"))

        self.stdout.write(self.style.SUCCESS("전체 주식 데이터 갱신 완료"))

    def update_price(self, stock, ticker):
        try:
            quote = fetch_stock_quote(ticker)

            if quote["current_price"] == 0:
                self.stdout.write(self.style.WARNING(f"{ticker} 현재가 데이터 없음"))
                return

            StockPrice.objects.update_or_create(
                stock=stock,
                defaults={
                    "current_price": quote["current_price"],
                    "currency": quote["currency"],
                    "change_rate": quote["change_rate"],
                    "change_amount": quote["change_amount"],
                    "volume": quote["volume"],
                },
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f"{ticker} 현재가 저장: ${quote['current_price']} ({quote['change_rate']}%)"
                )
            )

        except Exception as error:
            self.stdout.write(self.style.WARNING(f"{ticker} 현재가 갱신 실패: {error}"))

    def update_chart(self, stock, ticker):
        try:
            chart_points = fetch_stock_chart(ticker)

            if not chart_points:
                self.stdout.write(self.style.WARNING(f"{ticker} 차트 데이터 없음"))
                return

            StockChartPoint.objects.filter(stock=stock).delete()

            for point in chart_points:
                StockChartPoint.objects.create(
                    stock=stock,
                    time=point["time"],
                    price=point["price"],
                    volume=point["volume"],
                )

            self.stdout.write(
                self.style.SUCCESS(f"{ticker} 차트 데이터 {len(chart_points)}개 저장")
            )

        except Exception as error:
            self.stdout.write(self.style.WARNING(f"{ticker} 차트 갱신 실패: {error}"))