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

        summary_model_name = "csebuetnlp/mT5_multilingual_XLSum"
        print("1. 요약 모델 로딩 중...")
        self.summary_model = AutoModelForSeq2SeqLM.from_pretrained(summary_model_name)
        self.summary_tokenizer = AutoTokenizer.from_pretrained(summary_model_name, legacy=False)

        print("2. 금융 감성 분석 모델 로딩 중...")
        sentiment_model_name = "ProsusAI/finbert"
        finbert_model = AutoModelForSequenceClassification.from_pretrained(sentiment_model_name)
        finbert_tokenizer = AutoTokenizer.from_pretrained(sentiment_model_name)
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
        text = re.sub(r'http\S+|www\S+', '', text)
        text = re.sub(r'@\w+', '', text)
        text = re.sub(r'#\w+', '', text)
        text = re.sub(r'[^\w\s\.\,\!\?]', '', text)
        text = ' '.join(text.split())
        return text.strip()

    def _summarize(self, text: str) -> str:
        input_text = "en " + " ".join(text.split())
        inputs = self.summary_tokenizer(
            input_text,
            return_tensors="pt",
            max_length=512,
            truncation=True
        )
        input_len = inputs["input_ids"].shape[1]
        dynamic_max = max(20, min(80, input_len // 2))

        with torch.no_grad():
            summary_ids = self.summary_model.generate(
                inputs["input_ids"],
                max_new_tokens=dynamic_max,
                num_beams=4,
                early_stopping=True,
                no_repeat_ngram_size=2
            )
        return self.summary_tokenizer.decode(summary_ids[0], skip_special_tokens=True)

    def _translate_ko(self, text: str) -> str:
        try:
            return GoogleTranslator(source="en", target="ko").translate(text)
        except Exception:
            return ""

    def _extract_keywords(self, text: str) -> list:
        stopwords = {"the", "a", "an", "is", "are", "was", "were", "has", "have",
                     "had", "be", "been", "being", "in", "on", "at", "to", "for",
                     "of", "and", "or", "but", "as", "with", "its", "it", "this",
                     "that", "by", "from", "after", "while", "amid"}
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
            clean_text = self._preprocess(text)
            summary = self._summarize(clean_text).strip() or clean_text
            summary_ko = self._translate_ko(summary)

            sentiment_results = self.sentiment_analyzer(summary)[0]
            scores_raw = {item["label"].lower(): item["score"] for item in sentiment_results}

            total = sum(scores_raw.values())
            sentiment_scores = {
                "positive": round(scores_raw.get("positive", 0) / total * 100, 1),
                "negative": round(scores_raw.get("negative", 0) / total * 100, 1),
                "neutral":  round(scores_raw.get("neutral",  0) / total * 100, 1),
            }
            main_sentiment = max(sentiment_scores, key=sentiment_scores.get)
            keywords = self._extract_keywords(summary)

            return {
                "ticker": ticker,
                "summary": summary,
                "summary_ko": summary_ko,
                "main_sentiment": main_sentiment,
                "sentiment_scores": sentiment_scores,
                "keywords": keywords,
                "model_info": {
                    "summary_model": "mT5",
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
            req.post(url, json=result)
            print(f"[DB 저장 완료] {ticker}")
        except Exception as e:
            print(f"[DB 저장 실패] {e}")

        return result


if __name__ == "__main__":
    test_tweet = "🚀 $TSLA surges 5%!! @elonmusk #Tesla #stocks https://t.co/abc123 Strong earnings report beats Wall Street expectations. Investors are optimistic about growth outlook."

    processor = EOSAIProcessor()
    result = processor.process(test_tweet, ticker="TSLA")

    print("\n[나연의 EOA AI 파이프라인 분석 완료]")
    print(f"▶ ticker: {result['ticker']}")
    print(f"▶ summary: {result['summary']}")
    print(f"▶ summary_ko: {result['summary_ko']}")
    print(f"▶ main_sentiment: {result['main_sentiment']}")
    print(f"▶ sentiment_scores: {result['sentiment_scores']}")
    print(f"▶ keywords: {result['keywords']}")
    print(f"▶ analyzed_at: {result['analyzed_at']}")
    print("="*50)
    # 백엔드 POST 테스트
    processor.analyze_and_save(test_tweet, ticker="TSLA")