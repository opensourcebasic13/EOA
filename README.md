# EOA

EOA는 X 기반 해외주식 트렌드 분석 웹서비스입니다.

사용자가 관심 있는 해외주식을 검색하면 해당 종목의 현재 주가 정보, 차트 데이터, X 게시글 반응, AI 요약 및 감정 분석 결과를 한 화면에서 확인할 수 있습니다.

---

## 프로젝트 개요

본 프로젝트는 해외주식 데이터와 X 게시글 데이터를 기반으로 사용자가 관심 있는 종목의 실시간 시장 반응을 빠르게 파악할 수 있도록 돕는 서비스입니다.

주요 기능은 다음과 같습니다.

* 해외주식 현재가 및 등락률 조회
* 해외주식 차트 데이터 조회
* X 기반 종목 관련 게시글 수집
* 트윗량이 많은 종목 랭킹 조회
* 종목 검색
* 종목별 상세 정보 조회
* mT5 기반 게시글 요약
* FinBERT 기반 금융 감성 분석
* AI 분석 결과 저장 및 조회
* 회원가입 / 로그인 / 로그아웃
* 사용자별 관심 주식 관리
* Swagger 기반 API 문서 제공

---

## 기술 스택

| 구분              | 기술                                    |
| --------------- | ------------------------------------- |
| Frontend        | React, Vite                           |
| Backend         | Python, Django, Django REST Framework |
| Database        | MySQL                                 |
| Stock Data      | yfinance                              |
| Social Data     | X API Filtered Stream                 |
| AI Summary      | mT5                                   |
| AI Sentiment    | FinBERT                               |
| API Docs        | drf-spectacular, Swagger              |
| Auth            | DRF Token Authentication              |
| Version Control | Git, GitHub                           |

---

## 프로젝트 구조

```text
EOA/
├─ backend/
│  ├─ analysis/
│  │  └─ processor.py
│  ├─ config/
│  ├─ stocks/
│  │  ├─ management/
│  │  │  └─ commands/
│  │  │     ├─ update_stock_market.py
│  │  │     └─ run_ai_analysis.py
│  │  ├─ services/
│  │  │  └─ market_data.py
│  │  ├─ models.py
│  │  ├─ serializers.py
│  │  ├─ urls.py
│  │  └─ views.py
│  ├─ tweets/
│  │  ├─ management/
│  │  │  └─ commands/
│  │  │     └─ stream_x_posts.py
│  │  ├─ services/
│  │  │  └─ x_stream_client.py
│  │  ├─ models.py
│  │  └─ urls.py
│  ├─ users/
│  │  ├─ serializers.py
│  │  ├─ urls.py
│  │  └─ views.py
│  ├─ manage.py
│  ├─ requirements.txt
│  └─ .env.example
├─ frontend/
├─ README.md
└─ .gitignore
```

---

## 백엔드 실행 방법

### 1. 저장소 클론

```bash
git clone https://github.com/opensourcebasic13/EOA.git
cd EOA
```

---

### 2. 가상환경 생성 및 실행

```bash
python3 -m venv venv
source venv/bin/activate
```

---

### 3. 패키지 설치

```bash
cd backend
pip install -r requirements.txt
```

AI 모델을 실행하기 위해 `torch`, `transformers`, `sentencepiece`, `deep-translator`가 필요합니다.

---

### 4. 환경 변수 파일 생성

`backend/.env.example` 파일을 참고하여 `backend/.env` 파일을 생성합니다.

```env
SECRET_KEY=your_django_secret_key
DEBUG=True

DB_NAME=eoa_db
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=127.0.0.1
DB_PORT=3306

X_BEARER_TOKEN=your_x_api_bearer_token
```

주의: `.env` 파일은 DB 비밀번호와 X API 토큰이 포함되므로 GitHub에 올리지 않습니다.

---

### 5. MySQL 데이터베이스 생성

MySQL에 접속한 뒤 아래 명령어를 실행합니다.

```sql
CREATE DATABASE eoa_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

---

### 6. 마이그레이션 실행

```bash
python manage.py migrate
```

---

### 7. 샘플 데이터 생성

초기 종목 데이터가 없는 경우 아래 명령어를 실행합니다.

```bash
python manage.py seed_data
```

---

## 서버 실행

```bash
python manage.py runserver
```

백엔드 서버 주소는 다음과 같습니다.

```text
http://127.0.0.1:8000
```

---

## Swagger API 문서

백엔드 서버 실행 후 아래 주소에서 API 문서를 확인할 수 있습니다.

```text
http://127.0.0.1:8000/api/schema/swagger-ui/
```

---

## 프론트엔드 연동 설정

프론트엔드 `.env` 파일에 백엔드 주소를 설정합니다.

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

프론트엔드 실행 예시:

```bash
cd frontend
npm install
npm run dev
```

프론트엔드 개발 서버 주소:

```text
http://localhost:5173
```

---

## 주요 실행 명령어

### 1. 주식 데이터 갱신

yfinance를 사용하여 해외주식 10개 종목의 현재가, 등락률, 거래량, 차트 데이터를 갱신합니다.

```bash
python manage.py update_stock_market
```

---

### 2. 주식 데이터 자동 갱신

1분마다 주식 가격 데이터를 자동 갱신합니다.

```bash
python manage.py update_stock_market --loop --interval 1
```

---

### 3. X 게시글 수집

X Developer에 등록된 Filtered Stream Rule을 기반으로 종목 관련 게시글을 수집합니다.

```bash
python manage.py stream_x_posts
```

테스트용으로 5개만 수집하려면 다음과 같이 실행합니다.

```bash
python manage.py stream_x_posts --max-count 5
```

현재 등록된 X Stream Rule을 확인하려면 다음 명령어를 사용합니다.

```bash
python manage.py stream_x_posts --show-rules
```

---

### 4. X 게시글 수집 + AI 자동 업데이트

새로운 X 게시글이 들어올 때마다 AI 분석 결과를 자동으로 갱신합니다.

```bash
python manage.py stream_x_posts --auto-ai --ai-every 5
```

테스트용으로 5개 게시글만 수집하면서 매 게시글마다 AI를 업데이트하려면 다음과 같이 실행합니다.

```bash
python manage.py stream_x_posts --max-count 5 --auto-ai --ai-every 1
```

---

### 5. AI 분석 실행

저장된 트윗 데이터를 기반으로 mT5 요약과 FinBERT 감성 분석을 실행합니다.

특정 종목만 분석:

```bash
python manage.py run_ai_analysis --ticker TSLA
```

전체 종목 분석:

```bash
python manage.py run_ai_analysis --all
```

---

## 로컬 실행 터미널 구성

실시간 기능을 모두 확인하려면 터미널을 여러 개 사용합니다.

### 터미널 1: Django 백엔드 서버

```bash
cd backend
python manage.py runserver
```

### 터미널 2: 주식 가격 매분 갱신

```bash
cd backend
python manage.py update_stock_market --loop --interval 1
```

### 터미널 3: X Stream 수집 및 AI 자동 업데이트

```bash
cd backend
python manage.py stream_x_posts --auto-ai --ai-every 5
```

### 터미널 4: React 프론트엔드

```bash
cd frontend
npm run dev
```

---

## API 목록

### Health Check

| 기능       | Method | URL            |
| -------- | ------ | -------------- |
| 서버 상태 확인 | GET    | `/api/health/` |

---

### Auth API

| 기능      | Method | URL                  |
| ------- | ------ | -------------------- |
| 회원가입    | POST   | `/api/users/signup/` |
| 로그인     | POST   | `/api/users/login/`  |
| 로그아웃    | POST   | `/api/users/logout/` |
| 내 정보 조회 | GET    | `/api/users/me/`     |

로그인 성공 시 응답으로 Token이 반환됩니다.

```json
{
  "success": true,
  "message": "로그인에 성공했습니다.",
  "data": {
    "token": "token_value",
    "user": {
      "id": 1,
      "username": "testuser",
      "email": "test@example.com"
    }
  }
}
```

인증이 필요한 요청에는 아래 헤더를 포함해야 합니다.

```http
Authorization: Token token_value
```

---

### Stock API

| 기능              | Method | URL                              |
| --------------- | ------ | -------------------------------- |
| 트윗량 많은 주식 목록 조회 | GET    | `/api/stocks/trending/`          |
| 종목 검색           | GET    | `/api/stocks/search/?q=TSLA`     |
| 특정 주식 상세 조회     | GET    | `/api/stocks/{ticker}/`          |
| 특정 주식 차트 조회     | GET    | `/api/stocks/{ticker}/chart/`    |
| 특정 주식 AI 분석 조회  | GET    | `/api/stocks/{ticker}/analysis/` |
| 특정 주식 AI 분석 저장  | POST   | `/api/stocks/{ticker}/analysis/` |
| 특정 주식 통합 정보 조회  | GET    | `/api/stocks/{ticker}/overview/` |

---

### Watchlist API

| 기능       | Method | URL               |
| -------- | ------ | ----------------- |
| 관심 주식 조회 | GET    | `/api/watchlist/` |
| 관심 주식 추가 | POST   | `/api/watchlist/` |
| 관심 주식 삭제 | DELETE | `/api/watchlist/` |

관심 주식 추가 요청 예시:

```json
{
  "ticker": "TSLA"
}
```

관심 주식 삭제 요청 예시:

```json
{
  "ticker": "TSLA"
}
```

---

## 핵심 API: 종목 통합 정보

프론트엔드 상세 페이지에서는 아래 API 하나로 종목의 핵심 정보를 조회할 수 있습니다.

```text
GET /api/stocks/{ticker}/overview/
```

예시:

```text
GET /api/stocks/TSLA/overview/
```

응답에는 다음 정보가 포함됩니다.

```text
stock
price
chart
social
social.hot_tweets
ai_analysis
```

---

## AI 분석 데이터 형식

AI 분석 결과는 다음 형식으로 저장됩니다.

```json
{
  "summary": "English summary",
  "summary_ko": "한국어 요약",
  "main_sentiment": "positive",
  "sentiment_scores": {
    "positive": 62.5,
    "negative": 24.0,
    "neutral": 13.5
  },
  "keywords": ["tesla", "earnings", "growth"],
  "model_info": {
    "summary_model": "mT5",
    "sentiment_model": "FinBERT"
  }
}
```

---

## 현재 구현 상태

* Django 백엔드 프로젝트 구성
* MySQL 연동
* 주식, 주가, 차트, 트윗, AI 분석 모델 생성
* 해외주식 10개 종목 관리
* yfinance 기반 주식 데이터 갱신
* X API Filtered Stream 기반 게시글 수집
* X 게시글 저장 시 트윗량 자동 증가
* mT5 기반 요약
* FinBERT 기반 금융 감성 분석
* AI 분석 결과 DB 저장
* 새 X 게시글 수집 시 AI 자동 업데이트
* 회원가입 / 로그인 / 로그아웃
* DRF Token Authentication
* 사용자별 관심 주식 관리
* Swagger API 문서 제공
* React 프론트엔드 연동 가능 구조 구성

---

## 향후 개발 예정

* 프론트엔드 로그인 / 회원가입 API 연결
* 관심 주식 추가 / 삭제 버튼 연동
* 실시간 가격 반영을 위한 프론트 주기적 API 호출
* AI 요약 품질 개선
* X 게시글 필터링 고도화
* Redis / Celery 기반 백그라운드 작업 분리
* 배포 서버 구성
* 주요 해외주식 10개에서 100개로 확장

---

## 주의사항

* `.env` 파일은 절대 GitHub에 올리지 않습니다.
* `venv/` 폴더는 GitHub에 올리지 않습니다.
* `node_modules/` 폴더는 GitHub에 올리지 않습니다.
* X API Bearer Token은 외부에 공개하지 않습니다.
* AI 모델은 최초 실행 시 다운로드 시간이 오래 걸릴 수 있습니다.
* X Stream 수집은 등록된 X Developer Rule을 기준으로 동작합니다.
* 주식 가격은 yfinance 기반 데이터이므로 실제 거래소 데이터와 약간의 지연 또는 차이가 있을 수 있습니다.
