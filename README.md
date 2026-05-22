

# EOA

EOA는 X 기반 주식 트렌드 분석 웹서비스입니다.  
사용자가 관심 있는 주식을 검색하면 해당 주식의 현재 주가 정보, 트윗량, 차트 데이터, 핫한 트윗 정보를 제공합니다.

## 프로젝트 개요

본 프로젝트는 주식 데이터와 X 게시글 데이터를 기반으로 사용자가 관심 있는 종목의 실시간 트렌드를 확인할 수 있도록 하는 웹서비스입니다.

주요 기능은 다음과 같습니다.

- 실시간 트윗량이 많은 주식 조회
- 종목 검색
- 특정 주식의 현재가 정보 조회
- 특정 주식의 차트 데이터 조회
- 특정 주식 관련 핫한 트윗 조회
- 관심 주식 목록 조회

## 기술 스택

| 구분 | 기술 |
|---|---|
| Frontend | React |
| Backend | Python, Django, Django REST Framework |
| Database | MySQL |
| API 문서 | drf-spectacular, Swagger |
| Design | Figma |
| Version Control | Git, GitHub |

## 프로젝트 구조

```text
EOA/
├─ backend/
│  ├─ config/
│  ├─ stocks/
│  ├─ tweets/
│  ├─ users/
│  ├─ manage.py
│  ├─ requirements.txt
│  └─ .env.example
├─ README.md
└─ .gitignore
````

## 백엔드 실행 방법

### 1. 저장소 클론

```bash
git clone https://github.com/opensourcebasic13/EOA.git
cd EOA
```

### 2. 가상환경 생성 및 실행

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. 패키지 설치

```bash
cd backend
pip install -r requirements.txt
```

### 4. 환경 변수 파일 생성

`backend/.env.example` 파일을 참고하여 `backend/.env` 파일을 생성합니다.

```env
DB_NAME=eoa_db
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=127.0.0.1
DB_PORT=3306
```

주의: `.env` 파일은 DB 비밀번호가 포함되므로 GitHub에 올리지 않습니다.

### 5. MySQL 데이터베이스 생성

MySQL에 접속한 뒤 아래 명령어를 실행합니다.

```sql
CREATE DATABASE eoa_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 6. 마이그레이션 실행

```bash
python manage.py migrate
```

### 7. 서버 실행

```bash
python manage.py runserver
```

서버 실행 후 아래 주소에서 확인할 수 있습니다.

```text
http://127.0.0.1:8000/
```

## API 목록

| 기능              | Method | URL                                |
| --------------- | ------ | ---------------------------------- |
| 트윗량 많은 주식 목록 조회 | GET    | `/api/stocks/trending/`            |
| 종목 검색           | GET    | `/api/stocks/search/?q=검색어`        |
| 관심 주식 목록 조회     | GET    | `/api/watchlist/`                  |
| 특정 주식 상세 조회     | GET    | `/api/stocks/{ticker}/`            |
| 특정 주식 차트 조회     | GET    | `/api/stocks/{ticker}/chart/`      |
| 특정 주식 핫 트윗 조회   | GET    | `/api/stocks/{ticker}/tweets/hot/` |

## API 테스트 예시

### 트윗량 많은 주식 목록

```text
http://127.0.0.1:8000/api/stocks/trending/
```

### 종목 검색

```text
http://127.0.0.1:8000/api/stocks/search/?q=테슬라
```

### 테슬라 상세 정보

```text
http://127.0.0.1:8000/api/stocks/TSLA/
```

### 테슬라 차트 데이터

```text
http://127.0.0.1:8000/api/stocks/TSLA/chart/
```

### 테슬라 핫 트윗

```text
http://127.0.0.1:8000/api/stocks/TSLA/tweets/hot/
```

## 현재 구현 상태

* Django 프로젝트 초기 설정 완료
* MySQL 연동 완료
* 주식, 주가, 차트, 트윗 관련 모델 생성
* 더미 데이터 기반 API 구현
* 메인 페이지 및 상세 페이지에 필요한 기본 API 구현

## 추후 개발 예정

* React 프론트엔드 구현
* 로그인 및 회원가입 기능 구현
* 사용자별 관심 주식 저장 기능 구현
* 실제 주식 데이터 API 연동
* X API 기반 게시글 수집 기능 구현
* 감성 분석 및 키워드 분석 기능 고도화
* Redis, Celery 기반 백그라운드 수집 작업 추가

## 주의사항

* `.env` 파일은 절대 GitHub에 올리지 않습니다.
* `venv/` 폴더는 GitHub에 올리지 않습니다.
* `db.sqlite3`는 사용하지 않으며, 실제 데이터베이스는 MySQL을 사용합니다.



