NEGATIVE_KEYWORDS = [
    "불만", "화남", "짜증", "화가", "실망", "불편", "항의", "환불", "취소", "불친절", "답답", "짜증나", "싫다", "못하겠다"
]

def is_negative_sentiment(text: str) -> bool:
    return any(kw in text for kw in NEGATIVE_KEYWORDS) 