import { useEffect, useMemo, useState } from 'react'
import './App.css'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

function normalizeList(response) {
  if (Array.isArray(response)) return response
  if (Array.isArray(response?.data)) return response.data
  return []
}

function normalizeOverview(response) {
  return response?.data ?? response
}

function formatNumber(value) {
  if (value === null || value === undefined) return '-'
  return Number(value).toLocaleString()
}

function formatPrice(value, currency = 'USD') {
  if (value === null || value === undefined) return '-'
  return `${Number(value).toLocaleString(undefined, { maximumFractionDigits: 2 })} ${currency}`
}

function ChangeBadge({ value }) {
  const numberValue = Number(value ?? 0)
  const isUp = numberValue >= 0
  return (
    <span className={`change-badge ${isUp ? 'up' : 'down'}`}>
      {isUp ? '▲' : '▼'} {Math.abs(numberValue).toFixed(2)}%
    </span>
  )
}

function SentimentBadge({ sentiment }) {
  const labels = {
    positive: '긍정',
    negative: '부정',
    neutral: '중립',
  }
  return <span className={`sentiment ${sentiment || 'neutral'}`}>{labels[sentiment] || '중립'}</span>
}

function App() {
  const [trendingStocks, setTrendingStocks] = useState([])
  const [watchlist, setWatchlist] = useState([])
  const [selectedTicker, setSelectedTicker] = useState('TSLA')
  const [overview, setOverview] = useState(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    async function loadMainData() {
      try {
        const [trendingRes, watchlistRes] = await Promise.all([
          fetch(`${API_BASE_URL}/api/stocks/trending/`),
          fetch(`${API_BASE_URL}/api/watchlist/`),
        ])

        const trendingJson = await trendingRes.json()
        const watchlistJson = await watchlistRes.json()

        setTrendingStocks(normalizeList(trendingJson))
        setWatchlist(normalizeList(watchlistJson))
      } catch (err) {
        setError('메인 데이터를 불러오지 못했습니다. 백엔드 서버가 켜져 있는지 확인하세요.')
      }
    }

    loadMainData()
  }, [])

  useEffect(() => {
    async function loadOverview() {
      setLoading(true)
      setError('')
      try {
        const res = await fetch(`${API_BASE_URL}/api/stocks/${selectedTicker}/overview/`)
        const json = await res.json()

        if (!res.ok) {
          throw new Error(json?.message || '종목 정보를 불러오지 못했습니다.')
        }

        setOverview(normalizeOverview(json))
      } catch (err) {
        setError(err.message || '종목 정보를 불러오지 못했습니다.')
      } finally {
        setLoading(false)
      }
    }

    loadOverview()
  }, [selectedTicker])

  async function handleSearch(event) {
    event.preventDefault()

    const keyword = searchQuery.trim()
    if (!keyword) {
      setSearchResults([])
      return
    }

    try {
      const res = await fetch(`${API_BASE_URL}/api/stocks/search/?q=${encodeURIComponent(keyword)}`)
      const json = await res.json()
      const results = normalizeList(json)
      setSearchResults(results)

      if (results[0]?.ticker) {
        setSelectedTicker(results[0].ticker)
      }
    } catch (err) {
      setError('검색 결과를 불러오지 못했습니다.')
    }
  }

  const chartMax = useMemo(() => {
    const prices = overview?.chart?.map((point) => Number(point.price)) || []
    return Math.max(...prices, 1)
  }, [overview])

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">E</div>
          <div>
            <strong>EOA</strong>
            <span>Stock Intelligence</span>
          </div>
        </div>

        <section className="side-card">
          <h2>관심 주식</h2>
          <div className="watchlist">
            {watchlist.map((stock) => (
              <button
                key={stock.ticker}
                className={`watch-item ${selectedTicker === stock.ticker ? 'active' : ''}`}
                type="button"
                onClick={() => setSelectedTicker(stock.ticker)}
              >
                <div>
                  <strong>{stock.name}</strong>
                  <span>{stock.ticker}</span>
                </div>
                <div className="watch-price">
                  <span>{formatPrice(stock.current_price, stock.currency)}</span>
                  <ChangeBadge value={stock.price_change_rate} />
                </div>
              </button>
            ))}
          </div>
        </section>
      </aside>

      <main className="main">
        <header className="topbar">
          <form className="search" onSubmit={handleSearch}>
            <span>⌕</span>
            <input
              value={searchQuery}
              onChange={(event) => setSearchQuery(event.target.value)}
              placeholder="종목명 또는 티커 검색"
            />
            <button type="submit">검색</button>
          </form>
          <div className="profile">
            <div className="avatar">지</div>
            <div>
              <span>안녕하세요,</span>
              <strong>지피티님</strong>
            </div>
          </div>
        </header>

        {searchResults.length > 0 && (
          <section className="search-results">
            {searchResults.map((stock) => (
              <button key={stock.ticker} type="button" onClick={() => setSelectedTicker(stock.ticker)}>
                {stock.name} <span>{stock.ticker}</span>
              </button>
            ))}
          </section>
        )}

        {error && <div className="error-box">{error}</div>}

        <section className="dashboard-grid">
          <section className="panel trending-panel">
            <div className="panel-header">
              <div>
                <span className="eyebrow">REAL-TIME SOCIAL SIGNAL</span>
                <h1>실시간 트윗량 많은 주식</h1>
              </div>
              <span className="api-chip">/api/stocks/trending/</span>
            </div>

            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>순위</th>
                    <th>종목</th>
                    <th>트윗량</th>
                    <th>1시간 변화</th>
                    <th>현재가</th>
                    <th>주가 등락</th>
                  </tr>
                </thead>
                <tbody>
                  {trendingStocks.map((stock, index) => (
                    <tr key={stock.ticker} onClick={() => setSelectedTicker(stock.ticker)}>
                      <td>{stock.rank || index + 1}</td>
                      <td>
                        <strong>{stock.name}</strong>
                        <span>{stock.ticker}</span>
                      </td>
                      <td>{formatNumber(stock.tweet_volume)}</td>
                      <td><ChangeBadge value={stock.one_hour_change_rate} /></td>
                      <td>{formatPrice(stock.current_price, stock.currency)}</td>
                      <td><ChangeBadge value={stock.price_change_rate} /></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>

          <section className="panel detail-panel">
            {loading ? (
              <div className="loading">종목 상세 정보를 불러오는 중...</div>
            ) : overview ? (
              <>
                <div className="detail-head">
                  <div>
                    <span className="eyebrow">STOCK OVERVIEW</span>
                    <h2>{overview.stock?.name} <span>({overview.stock?.ticker})</span></h2>
                    <p>{overview.stock?.market} · 실시간 주가 및 핫한 트윗</p>
                  </div>
                  <div className="price-card">
                    <strong>{formatPrice(overview.price?.current_price, overview.price?.currency)}</strong>
                    <ChangeBadge value={overview.price?.change_rate} />
                  </div>
                </div>

                <div className="mini-chart">
                  {(overview.chart || []).map((point, index) => (
                    <div key={`${point.time}-${index}`} className="bar-wrap">
                      <div
                        className="bar"
                        style={{ height: `${Math.max((Number(point.price) / chartMax) * 100, 8)}%` }}
                        title={`${point.price}`}
                      />
                    </div>
                  ))}
                </div>

                <div className="analysis-card">
                  <div className="analysis-top">
                    <h3>AI 요약</h3>
                    <SentimentBadge sentiment={overview.ai_analysis?.main_sentiment} />
                  </div>
                  <p>{overview.ai_analysis?.summary_ko || 'AI 분석 결과가 아직 없습니다.'}</p>
                  <div className="keywords">
                    {(overview.ai_analysis?.keywords || []).map((keyword) => (
                      <span key={keyword}>#{keyword}</span>
                    ))}
                  </div>
                </div>

                <section className="tweets">
                  <h3>지금 핫한 트윗</h3>
                  {(overview.social?.hot_tweets || []).map((tweet, index) => (
                    <article key={`${tweet.author_handle}-${index}`} className="tweet-card">
                      <div className="tweet-avatar">{tweet.author_name?.slice(0, 1)}</div>
                      <div>
                        <div className="tweet-meta">
                          <strong>{tweet.author_name}</strong>
                          <span>{tweet.author_handle}</span>
                          <SentimentBadge sentiment={tweet.sentiment} />
                        </div>
                        <p>{tweet.content}</p>
                        <div className="tweet-actions">
                          <span>좋아요 {tweet.like_count}</span>
                          <span>댓글 {tweet.reply_count}</span>
                          <span>리포스트 {tweet.repost_count}</span>
                        </div>
                      </div>
                    </article>
                  ))}
                </section>
              </>
            ) : null}
          </section>
        </section>
      </main>
    </div>
  )
}

export default App
