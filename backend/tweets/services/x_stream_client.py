import json
import os
import requests
import re


X_STREAM_URL = "https://api.x.com/2/tweets/search/stream"
X_RULES_URL = "https://api.x.com/2/tweets/search/stream/rules"


SUPPORTED_STOCKS = [
    {"ticker": "TSLA", "name": "Tesla"},
    {"ticker": "NVDA", "name": "NVIDIA"},
    {"ticker": "AAPL", "name": "Apple"},
    {"ticker": "MSFT", "name": "Microsoft"},
    {"ticker": "AMZN", "name": "Amazon"},
    {"ticker": "GOOGL", "name": "Alphabet"},
    {"ticker": "META", "name": "Meta"},
    {"ticker": "AMD", "name": "AMD"},
    {"ticker": "PLTR", "name": "Palantir"},
    {"ticker": "NFLX", "name": "Netflix"},
]


def get_headers():
    bearer_token = os.getenv("X_BEARER_TOKEN", "").strip()

    if not bearer_token:
        raise ValueError("X_BEARER_TOKEN이 .env에 설정되어 있지 않습니다.")

    return {
        "Authorization": f"Bearer {bearer_token}",
    }


def get_stream_rules():
    response = requests.get(
        X_RULES_URL,
        headers=get_headers(),
        timeout=15,
    )
    response.raise_for_status()
    return response.json()


def connect_stream():
    params = {
        "tweet.fields": "created_at,public_metrics,lang",
        "expansions": "author_id",
        "user.fields": "username,name",
    }

    response = requests.get(
        X_STREAM_URL,
        headers=get_headers(),
        params=params,
        stream=True,
        timeout=90,
    )

    response.raise_for_status()

    for line in response.iter_lines():
        if not line:
            continue

        yield json.loads(line.decode("utf-8"))


def extract_ticker_from_payload(payload):
    text = payload.get("data", {}).get("text", "")
    text_lower = text.lower()

    supported_tickers = {
        stock["ticker"].upper()
        for stock in SUPPORTED_STOCKS
    }

    # 1. matching_rules tag가 진짜 티커일 때만 사용
    matching_rules = payload.get("matching_rules", [])

    if matching_rules:
        tag = matching_rules[0].get("tag", "").upper().strip()

        if tag in supported_tickers:
            return tag

    # 2. tag가 "US STOCKS 10" 같은 그룹명이면 트윗 본문에서 티커/종목명 추출
    for stock in SUPPORTED_STOCKS:
        ticker = stock["ticker"]
        ticker_lower = ticker.lower()
        name_lower = stock["name"].lower()

        # $TSLA, TSLA 같은 패턴 탐지
        ticker_pattern = rf"(?<![A-Za-z0-9])\$?{re.escape(ticker_lower)}(?![A-Za-z0-9])"

        if re.search(ticker_pattern, text_lower):
            return ticker

        # Tesla, NVIDIA 같은 회사명 탐지
        if name_lower in text_lower:
            return ticker

    return None


def extract_author_info(payload):
    includes = payload.get("includes", {})
    users = includes.get("users", [])

    if not users:
        return {
            "author_name": "X User",
            "author_handle": "@x_user",
        }

    user = users[0]
    username = user.get("username", "x_user")

    return {
        "author_name": user.get("name", "X User"),
        "author_handle": f"@{username}",
    }