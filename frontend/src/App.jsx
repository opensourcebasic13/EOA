import { useEffect, useState } from "react";
import "./App.css";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

function App() {
  const [trendingStocks, setTrendingStocks] = useState([]);
  const [watchlist, setWatchlist] = useState([]);
  const [selectedTicker, setSelectedTicker] = useState("TSLA");
  const [overview, setOverview] = useState(null);
  const [searchKeyword, setSearchKeyword] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [mainError, setMainError] = useState("");
  const [detailError, setDetailError] = useState("");
  const [loadingDetail, setLoadingDetail] = useState(false);

  useEffect(() => {
    fetchMainData();
    fetchOverview("TSLA");
  }, []);

  const fetchMainData = async () => {
    try {
      const [trendingRes, watchlistRes] = await Promise.all([
        fetch(`${API_BASE_URL}/api/stocks/trending/`),
        fetch(`${API_BASE_URL}/api/watchlist/`),
      ]);

      if (!trendingRes.ok || !watchlistRes.ok) {
        throw new Error("메인 데이터 요청 실패");
      }

      const trendingData = await trendingRes.json();
      const watchlistData = await watchlistRes.json();

      setTrendingStocks(trendingData);
      setWatchlist(watchlistData);
      setMainError("");
    } catch (error) {
      console.error(error);
      setMainError("메인 데이터를 불러오지 못했습니다. 백엔드 서버가 켜져 있는지 확인하세요.");
    }
  };

  const fetchOverview = async (ticker) => {
    try {
      setLoadingDetail(true);
      setDetailError("");
      setSelectedTicker(ticker);

      const response = await fetch(`${API_BASE_URL}/api/stocks/${ticker}/overview/`);

      if (!response.ok) {
        throw new Error("상세 데이터 요청 실패");
      }

      const result = await response.json();
      setOverview(result.data);
    } catch (error) {
      console.error(error);
      setDetailError(`${ticker} 상세 정보를 불러오지 못했습니다.`);
      setOverview(null);
    } finally {
      setLoadingDetail(false);
    }
  };

  const handleSearch = async (event) => {
    event.preventDefault();

    const keyword = searchKeyword.trim();

    if (!keyword) {
      setSearchResults([]);
      return;
    }

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/stocks/search/?q=${encodeURIComponent(keyword)}`
      );

      if (!response.ok) {
        throw new Error("검색 실패");
      }

      const data = await response.json();
      setSearchResults(data);
    } catch (error) {
      console.error(error);
      setSearchResults([]);
    }
  };

  const getSentimentLabel = (sentiment) => {
    if (sentiment === "positive") return "긍정";
    if (sentiment === "negative") return "부정";
    return "중립";
  };

  const formatNumber = (value) => {
    if (value === null || value === undefined) return "-";
    return Number(value).toLocaleString();
  };

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          <div className="logo">EOA</div>
          <p>X 기반 해외주식 트렌드 분석</p>
        </div>

        <section className="side-section">
          <h3>관심 주식</h3>

          {watchlist.length === 0 ? (
            <p className="empty-text">관심 주식이 없습니다.</p>
          ) : (
            <ul className="watchlist">
              {watchlist.map((stock) => (
                <li
                  key={stock.ticker}
                  className={selectedTicker === stock.ticker ? "active" : ""}
                  onClick={() => fetchOverview(stock.ticker)}
                >
                  <span>{stock.ticker}</span>
                  <small>{stock.name}</small>
                </li>
              ))}
            </ul>
          )}
        </section>
      </aside>

      <main className="main">
        <header className="topbar">
          <form className="search-box" onSubmit={handleSearch}>
            <input
              value={searchKeyword}
              onChange={(e) => setSearchKeyword(e.target.value)}
              placeholder="종목명 또는 티커 검색 예: TSLA, NVDA"
            />
            <button type="submit">검색</button>
          </form>

          <div className="profile">지피티님</div>
        </header>

        {searchResults.length > 0 && (
          <section className="search-results">
            <h3>검색 결과</h3>
            <div className="result-list">
              {searchResults.map((stock) => (
                <button key={stock.ticker} onClick={() => fetchOverview(stock.ticker)}>
                  {stock.name} ({stock.ticker})
                </button>
              ))}
            </div>
          </section>
        )}

        {mainError && <div className="error-box">{mainError}</div>}

        <section className="content-grid">
          <section className="card trending-card">
            <div className="card-header">
              <h2>실시간 트윗량 많은 주식</h2>
              <span>Top 10</span>
            </div>

            <table>
              <thead>
                <tr>
                  <th>순위</th>
                  <th>종목</th>
                  <th>트윗량</th>
                  <th>1시간 변화</th>
                  <th>주가 등락</th>
                </tr>
              </thead>
              <tbody>
                {trendingStocks.map((stock, index) => (
                  <tr key={stock.ticker} onClick={() => fetchOverview(stock.ticker)}>
                    <td>{stock.rank || index + 1}</td>
                    <td>
                      <strong>{stock.ticker}</strong>
                      <span>{stock.name}</span>
                    </td>
                    <td>{formatNumber(stock.tweet_volume)}</td>
                    <td className={Number(stock.one_hour_change_rate) >= 0 ? "up" : "down"}>
                      {stock.one_hour_change_rate}%
                    </td>
                    <td className={Number(stock.price_change_rate) >= 0 ? "up" : "down"}>
                      {stock.price_change_rate ?? "-"}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>

          <section className="card detail-card">
            {loadingDetail && <p>상세 정보를 불러오는 중...</p>}

            {detailError && <div className="error-box">{detailError}</div>}

            {overview && (
              <>
                <div className="detail-title">
                  <div>
                    <h2>
                      {overview.stock.name} <span>{overview.stock.ticker}</span>
                    </h2>
                    <p>{overview.stock.market}</p>
                  </div>

                  <div className="price-box">
                    <strong>
                      {overview.price.current_price
                        ? `$${overview.price.current_price}`
                        : "-"}
                    </strong>
                    <span className={Number(overview.price.change_rate) >= 0 ? "up" : "down"}>
                      {overview.price.change_rate ?? 0}%
                    </span>
                  </div>
                </div>

                <div className="mini-chart">
                  <h3>차트 데이터</h3>
                  {overview.chart.length === 0 ? (
                    <p className="empty-text">차트 데이터가 없습니다.</p>
                  ) : (
                    <div className="chart-bars">
                      {overview.chart.map((point, index) => (
                        <div key={index} className="chart-point">
                          <div
                            className="bar"
                            style={{
                              height: `${Math.max(20, Number(point.price) % 100)}px`,
                            }}
                          />
                          <small>{Number(point.price).toFixed(1)}</small>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                <div className="ai-box">
                  <h3>AI 요약 및 감정 분석</h3>

                  {overview.ai_analysis ? (
                    <>
                      <p>{overview.ai_analysis.summary_ko}</p>

                      <div className="sentiment-row">
                        <span className={`sentiment ${overview.ai_analysis.main_sentiment}`}>
                          {getSentimentLabel(overview.ai_analysis.main_sentiment)}
                        </span>
                        <span>긍정 {overview.ai_analysis.sentiment_scores.positive}%</span>
                        <span>부정 {overview.ai_analysis.sentiment_scores.negative}%</span>
                        <span>중립 {overview.ai_analysis.sentiment_scores.neutral}%</span>
                      </div>

                      <div className="keywords">
                        {overview.ai_analysis.keywords.map((keyword) => (
                          <span key={keyword}>#{keyword}</span>
                        ))}
                      </div>
                    </>
                  ) : (
                    <p className="empty-text">AI 분석 결과가 없습니다.</p>
                  )}
                </div>

                <div className="tweets-box">
                  <h3>핫한 트윗</h3>

                  {overview.social.hot_tweets.length === 0 ? (
                    <p className="empty-text">트윗 데이터가 없습니다.</p>
                  ) : (
                    overview.social.hot_tweets.map((tweet, index) => (
                      <div className="tweet" key={index}>
                        <div className="tweet-header">
                          <strong>{tweet.author_name}</strong>
                          <span>{tweet.author_handle}</span>
                        </div>
                        <p>{tweet.content}</p>
                        <div className="tweet-footer">
                          <span>좋아요 {formatNumber(tweet.like_count)}</span>
                          <span>리포스트 {formatNumber(tweet.repost_count)}</span>
                          <span>{getSentimentLabel(tweet.sentiment)}</span>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </>
            )}
          </section>
        </section>
      </main>
    </div>
  );
}

export default App;
