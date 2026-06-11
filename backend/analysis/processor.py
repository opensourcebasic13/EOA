import torch
import re
from datetime import datetime, timezone
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, AutoModelForSequenceClassification, pipeline
from deep_translator import GoogleTranslator


class EOSAIProcessor:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EOSAIProcessor, cls).__new__(cls)
            cls._instance._init_models()
        return cls._instance

    def _init_models(self):
        print("\n" + "="*50)
        print("EOA AI ENGINE: 초기화 및 모델 로딩 중...")
        print("담당: 정보통계학과 나연 (AI Lead)")
        print("="*50)

        print("1. 요약 모델 로딩 중... (facebook/bart-large-cnn)")
        self.summary_tokenizer = AutoTokenizer.from_pretrained("facebook/bart-large-cnn")
        self.summary_model = AutoModelForSeq2SeqLM.from_pretrained("facebook/bart-large-cnn")

        print("2. 금융 감성 분석 모델 로딩 중... (ProsusAI/finbert)")
        finbert_model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")
        finbert_tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
        self.sentiment_analyzer = pipeline(
            "sentiment-analysis",
            model=finbert_model,
            tokenizer=finbert_tokenizer,
            top_k=None
        )

        print("="*50)
        print("EOA AI ENGINE: 모든 오픈소스 모델 로드 완료.")
        print("="*50 + "\n")

    def _preprocess(self, text: str) -> str:
        # URL 제거
        text = re.sub(r'http\S+|www\S+', '', text)
        # @멘션 제거
        text = re.sub(r'@\w+', '', text)
        # #TSLA → TSLA, $TSLA → TSLA (기호만 제거, 단어 유지)
        text = re.sub(r'#(\w+)', r'\1', text)
        text = re.sub(r'\$(\w+)', r'\1', text)
        # 금융 문맥 기호 유지 (%, +, - 포함)
        text = re.sub(r'[^\w\s\.\,\!\?\%\+\-]', '', text)
        text = ' '.join(text.split())
        return text.strip()

    def _summarize(self, text: str) -> str:
        inputs = self.summary_tokenizer(
            text,
            return_tensors="pt",
            max_length=1024,
            truncation=True
        )
        with torch.no_grad():
            summary_ids = self.summary_model.generate(
                inputs["input_ids"],
                max_new_tokens=60,
                min_length=20,
                num_beams=4,
                early_stopping=True,
                no_repeat_ngram_size=3
            )
        return self.summary_tokenizer.decode(summary_ids[0], skip_special_tokens=True)

    def _analyze_sentiment_batch(self, texts: list) -> dict:
        """트윗 각각 FinBERT 분석 후 앙상블 평균"""
        all_scores = {"positive": 0.0, "negative": 0.0, "neutral": 0.0}
        count = 0

        for text in texts[:20]:
            if not text.strip():
                continue
            try:
                result = self.sentiment_analyzer(
                    text,
                    truncation=True,
                    max_length=512
                )[0]
                if isinstance(result, dict):
                    result = [result]
                for item in result:
                    label = item["label"].lower()
                    all_scores[label] = all_scores.get(label, 0) + item["score"]
                count += 1
            except Exception:
                continue

        if count == 0:
            return {"positive": 33.3, "negative": 33.3, "neutral": 33.4}

        total = sum(all_scores.values())
        return {
            "positive": round(all_scores["positive"] / total * 100, 1),
            "negative": round(all_scores["negative"] / total * 100, 1),
            "neutral": round(all_scores["neutral"] / total * 100, 1),
        }

    def _get_dominant_sentiment(self, sentiment_scores: dict) -> str:
        """전체 비율 기준 대표 감성"""
        return max(sentiment_scores, key=sentiment_scores.get)

    def _get_investment_direction(self, sentiment_scores: dict) -> str:
        """
        투자 방향성: 중립 제외하고 긍정/부정만 비교
        X 게시글 특성상 중립·질문·단순언급이 많으므로
        방향성 있는 트윗 기준으로 판단
        """
        positive = sentiment_scores.get("positive", 0)
        negative = sentiment_scores.get("negative", 0)
        if positive > negative:
            return "positive"
        elif negative > positive:
            return "negative"
        else:
            return "neutral"

    def _translate_ko(self, text: str) -> str:
        try:
            return GoogleTranslator(source="en", target="ko").translate(text)
        except Exception:
            return ""

    def _extract_keywords(self, text: str) -> list:
        stopwords = {"the", "a", "an", "is", "are", "was", "were", "has", "have",
                     "had", "be", "been", "being", "in", "on", "at", "to", "for",
                     "of", "and", "or", "but", "as", "with", "its", "it", "this",
                     "that", "by", "from", "after", "while", "amid", "more", "than",
                     "just", "will", "can", "all", "not", "still", "long", "been",
                     "what", "let", "see", "new", "around", "level", "today"}
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        filtered = [w for w in words if w not in stopwords]
        freq = {}
        for w in filtered:
            freq[w] = freq.get(w, 0) + 1
        sorted_words = sorted(freq, key=freq.get, reverse=True)
        return sorted_words[:5]

    def process(self, text: str, ticker: str = "UNKNOWN") -> dict:
        if not text or len(text.strip()) == 0:
            return {"error": "입력 텍스트가 비어있습니다."}

        try:
            # 1. 전처리
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            clean_lines = [self._preprocess(line) for line in lines if line.strip()]

            # 2. BART 요약
            summary_input = ' '.join(clean_lines[:10])
            summary = self._summarize(summary_input).strip()
            if not summary and clean_lines:
                summary = clean_lines[0]

            # 3. FinBERT 앙상블 감성분석
            sentiment_scores = self._analyze_sentiment_batch(clean_lines)

            # 4. 대표 감성 + 투자 방향성 분리
            dominant_sentiment = self._get_dominant_sentiment(sentiment_scores)
            investment_direction = self._get_investment_direction(sentiment_scores)

            # 5. 한국어 번역
            summary_ko = self._translate_ko(summary)

            # 6. 키워드 추출
            keywords = self._extract_keywords(' '.join(clean_lines))

            return {
                "ticker": ticker,
                "summary": summary,
                "summary_ko": summary_ko,
                "main_sentiment": investment_direction,      # 백엔드 호환용
                "dominant_sentiment": dominant_sentiment,    # 실제 대표 감성
                "investment_direction": investment_direction, # 투자 방향성
                "sentiment_scores": sentiment_scores,
                "keywords": keywords,
                "model_info": {
                    "summary_model": "BART",
                    "sentiment_model": "FinBERT"
                },
                "analyzed_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            }

        except Exception as e:
            print(f"[AI ENGINE ERROR] {e}")
            return {"error": str(e)}

    def analyze_and_save(self, text: str, ticker: str) -> dict:
        result = self.process(text, ticker)
        if "error" in result:
            return result

        try:
            import requests as req
            url = f"http://127.0.0.1:8000/api/stocks/{ticker}/analysis/"
            response = req.post(url, json=result, timeout=5)
            response.raise_for_status()
            print(f"[DB 저장 완료] {ticker}")
        except Exception as e:
            print(f"[DB 저장 실패] {e}")

        return result


if __name__ == "__main__":
    test_tweets = """Tesla just crushed Q2 earnings! Delivery numbers smashed expectations. $TSLA is the clear EV leader.
Tesla volume spike detected. Options flow heavily bullish. Price target raised to $250. $TSLA
Tesla FSD v13 is miles ahead of any competitor. Ford's BlueCruise can't touch it. Long $TSLA.
Bought more $TSLA on the dip. Tesla's energy business alone is worth more than Ford's entire market cap.
Tesla Cybertruck production ramping faster than expected. Demand backlog still strong. $TSLA breakout incoming.
Not selling my $TSLA. Five year horizon. Autonomous driving will reshape everything.
Tesla valuation still seems stretched at these levels. PE ratio hard to justify. $TSLA
Watching $TSLA closely today. Chart looking interesting around this level."""

    processor = EOSAIProcessor()
    result = processor.process(test_tweets, ticker="TSLA")

    print("\n[나연의 EOA AI 파이프라인 분석 완료]")
    print(f"▶ ticker: {result['ticker']}")
    print(f"▶ summary: {result['summary']}")
    print(f"▶ summary_ko: {result['summary_ko']}")
    print(f"▶ dominant_sentiment: {result['dominant_sentiment']} (전체 비율 기준)")
    print(f"▶ investment_direction: {result['investment_direction']} (중립 제외 방향성)")
    print(f"▶ sentiment_scores: {result['sentiment_scores']}")
    print(f"▶ keywords: {result['keywords']}")
    print(f"▶ analyzed_at: {result['analyzed_at']}")
    print("="*50)
    processor.analyze_and_save(test_tweets, ticker="TSLA")