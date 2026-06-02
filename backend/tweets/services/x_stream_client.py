import os
import requests


X_RECENT_SEARCH_URL = "https://api.x.com/2/tweets/search/recent"


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


def build_query(ticker: str, name: str) -> str:
    return f'(${ticker} OR {ticker} OR "{name}") lang:en -is:retweet'


def fetch_recent_posts(ticker: str, name: str, max_results: int = 10) -> list[dict]:
    params = {
        "query": build_query(ticker, name),
        "max_results": max_results,
        "tweet.fields": "created_at,public_metrics,lang",
        "expansions": "author_id",
        "user.fields": "username,name",
    }

    response = requests.get(
        X_RECENT_SEARCH_URL,
        headers=get_headers(),
        params=params,
        timeout=15,
    )

    response.raise_for_status()
    payload = response.json()

    users = {
        user["id"]: user
        for user in payload.get("includes", {}).get("users", [])
    }

    posts = []

    for item in payload.get("data", []):
        metrics = item.get("public_metrics", {})
        author = users.get(item.get("author_id"), {})

        username = author.get("username", "x_user")

        posts.append({
            "content": item.get("text", ""),
            "posted_at": item.get("created_at"),
            "author_name": author.get("name", "X User"),
            "author_handle": f"@{username}",
            "like_count": metrics.get("like_count", 0),
            "reply_count": metrics.get("reply_count", 0),
            "repost_count": metrics.get("retweet_count", 0),
        })

    return posts


def build_sample_posts(ticker: str, name: str) -> list[dict]:
    return [
        {
            "content": f"{name} is gaining attention as investors discuss recent momentum and market expectations.",
            "posted_at": None,
            "author_name": "X Sample User",
            "author_handle": "@x_sample",
            "like_count": 512,
            "reply_count": 34,
            "repost_count": 128,
        },
        {
            "content": f"{ticker} is being mentioned frequently with AI, earnings, and growth-related keywords today.",
            "posted_at": None,
            "author_name": "Market Watcher",
            "author_handle": "@market_watcher",
            "like_count": 401,
            "reply_count": 28,
            "repost_count": 96,
        },
        {
            "content": f"Some traders remain cautious about {ticker} due to valuation and short-term volatility.",
            "posted_at": None,
            "author_name": "Risk Monitor",
            "author_handle": "@risk_monitor",
            "like_count": 193,
            "reply_count": 51,
            "repost_count": 62,
        },
    ]