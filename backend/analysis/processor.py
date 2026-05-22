import os
import torch
from transformers import pipeline, AutoModelForSeq2SeqLM, AutoTokenizer, AutoModelForSequenceClassification

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
        
        # 1. mT5 요약 모델 설정 (최신 버전 text-generation 단일화 규격 반영)
        summary_model_name = "csebuetnlp/mT5_multilingual_XLSum"
        print("1. 요약 모델 로딩 중...")
        
        t5_model = AutoModelForSeq2SeqLM.from_pretrained(summary_model_name)
        t5_tokenizer = AutoTokenizer.from_pretrained(summary_model_name, legacy=False)
        
        # 최신 허깅페이스 라이브러리 지원 목록에 맞춰 'text-generation'으로 매핑합니다.
        self.summarizer = pipeline(
            "text-generation",
            model=t5_model, 
            tokenizer=t5_tokenizer
        )
        
        # 2. FinBERT 감성 분석 모델 설정
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

    def process(self, text: str) -> dict:
        if not text or len(text.strip()) == 0:
            return {"summary": "", "score": 0.0, "label": "neutral"}

        try:
            # text-generation 태스크 규칙에 맞춰 파라미터 전달 (return_full_text=False로 원문 출력 방지)
            summary_output = self.summarizer(
                text, 
                max_new_tokens=40,
                do_sample=False,
                return_full_text=False
            )[0]
            
            summary = summary_output.get("generated_text") or summary_output.get("summary_text") or text
            summary = summary.strip()

            # 금융 특화 감성 분석 수행
            sentiment = self.sentiment_analyzer(summary)[0]
            
            # 투자 시그널 정량적 수치화 (-1.0 ~ 1.0)
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
    # 데이터 파이프라인 연동 검증용 가상 주식 트윗
    test_tweet = "TSLA stock spikes 5% after hours as retail traders surge on social media platforms."
    
    processor = EOSAIProcessor()
    result = processor.process(test_tweet)
    
    print("\n[나연의 EOA AI 파이프라인 분석 완료]")
    print(f"▶ 원문 트윗: {test_tweet}")
    print(f"▶ AI 핵심 요약: {result['summary']}")
    print(f"▶ 투자 시그널 점수: {result['score']} ({result['label']})")
    print("="*50)