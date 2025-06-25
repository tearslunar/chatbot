from app.utils.gemini import get_gemini_answer

NEGATIVE_KEYWORDS = [
    "불만", "화남", "짜증", "화가", "실망", "불편", "항의", "환불", "취소", "불친절", "답답", "짜증나", "싫다", "못하겠다"
]

NEGATIVE_LABELS = ["부정", "불만", "분노", "불안"]

def is_negative_sentiment(text: str) -> bool:
    return any(kw in text for kw in NEGATIVE_KEYWORDS)

# LLM 프롬프트 기반 감성분석

def analyze_sentiment_llm(text: str, model_name: str) -> str:
    prompt = (
        "아래 문장의 감정을 한 단어(긍정/부정/불만/분노/불안/중립 등)로만 답해줘.\n"
        f"문장: {text}"
    )
    result = get_gemini_answer(prompt, model_name)
    return result.strip().split()[0] if result else ""

def is_negative_sentiment_llm(text: str, model_name: str) -> bool:
    label = analyze_sentiment_llm(text, model_name)
    return any(lbl in label for lbl in NEGATIVE_LABELS) 