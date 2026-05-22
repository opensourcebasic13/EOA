import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, AutoModelForSequenceClassification, pipeline

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

        # 1. mT5 요약 모델 - pipeline() 없이 직접 로드
        summary_model_name = "csebuetnlp/mT5_multilingual_XLSum"
        print("1. 요약 모델 로딩 중...")
        self.summary_model = AutoModelForSeq2SeqLM.from_pretrained(summary_model_name)
        self.summary_tokenizer = AutoTokenizer.from_pretrained(summary_model_name, legacy=False)

        # 2. FinBERT 감성 분석 모델
        print("2. 금융 감성 분석 모델 로딩 중...")
        sentiment_model_name = "ProsusAI/finbert"
        finbert_model = AutoModelForSequenceClassification.from_pretrained(sentiment_model_name)
        finbert_tokenizer = AutoTokenizer.from_pretrained(sentiment_model_name)
        self.sentiment_analyzer = pipeline(
            "sentiment-analysis",
            model=finbert_model,
            tokenizer=finbert_tokenizer
        )

        print("="*50)
        print("EOA AI ENGINE: 모든 오픈소스 모델 로드 완료.")
        print("="*50 + "\n")

    def _summarize(self, text: str) -> str:
        # mT5-XLSum 전용 언어 태그 필수
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

    def process(self, text: str) -> dict:
        if not text or len(text.strip()) == 0:
            return {"summary": "", "score": 0.0, "label": "neutral"}

        try:
            summary = self._summarize(text).strip()
            if not summary:
                summary = text

            sentiment = self.sentiment_analyzer(summary)[0]
            raw_score = sentiment["score"]
            label = sentiment["label"].lower()

            if label == "negative":
                score = -raw_score
            elif label == "neutral":
                score = 0.0
            else:
                score = raw_score

            return {
                "summary": summary,
                "score": round(score, 2),
                "label": label
            }

        except Exception as e:
            print(f"[AI ENGINE ERROR] 실행 중 예외 발생: {e}")
            return {
                "summary": text[:40] + "...",
                "score": 0.0,
                "label": "error"
            }


if __name__ == "__main__":
    test_tweet = "TSLA stock spikes 5% after hours as retail traders surge on social media platforms."

    processor = EOSAIProcessor()
    result = processor.process(test_tweet)

    print("\n[나연의 EOA AI 파이프라인 분석 완료]")
    print(f"▶ 원문 트윗: {test_tweet}")
    print(f"▶ AI 핵심 요약: {result['summary']}")
    print(f"▶ 투자 시그널 점수: {result['score']} ({result['label']})")
    print("="*50)