import yfinance as yf


def fetch_stock_quote(ticker: str) -> dict:
    stock = yf.Ticker(ticker)

    current_price = 0
    previous_close = 0
    volume = 0

    # 1차 시도: fast_info에서 현재가 가져오기
    try:
        fast_info = stock.fast_info

        current_price = (
            fast_info.get("last_price")
            or fast_info.get("lastPrice")
            or fast_info.get("regular_market_price")
            or 0
        )

        previous_close = (
            fast_info.get("previous_close")
            or fast_info.get("previousClose")
            or 0
        )

        volume = (
            fast_info.get("last_volume")
            or fast_info.get("lastVolume")
            or 0
        )

    except Exception:
        pass

    # 2차 시도: fast_info가 비어 있으면 최근 5일 종가 사용
    if not current_price or current_price == 0:
        history = stock.history(period="5d", interval="1d")

        if not history.empty:
            closes = history["Close"].dropna()
            volumes = history["Volume"].dropna()

            if len(closes) >= 1:
                current_price = closes.iloc[-1]

            if len(closes) >= 2:
                previous_close = closes.iloc[-2]
            else:
                previous_close = current_price

            if len(volumes) >= 1:
                volume = volumes.iloc[-1]

    if current_price and previous_close:
        change_amount = float(current_price) - float(previous_close)
        change_rate = (change_amount / float(previous_close)) * 100
    else:
        change_amount = 0
        change_rate = 0

    return {
        "current_price": round(float(current_price or 0), 2),
        "change_amount": round(float(change_amount or 0), 2),
        "change_rate": round(float(change_rate or 0), 2),
        "volume": int(volume or 0),
        "currency": "USD",
    }


def fetch_stock_chart(ticker: str, period: str = "7d", interval: str = "1d") -> list[dict]:
    stock = yf.Ticker(ticker)
    history = stock.history(period=period, interval=interval)

    chart_points = []

    if history.empty:
        return chart_points

    for index, row in history.iterrows():
        chart_points.append({
            "time": index.to_pydatetime(),
            "price": round(float(row["Close"]), 2),
            "volume": int(row["Volume"] or 0),
        })

    return chart_points