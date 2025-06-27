import os
import requests

NEGATIVE_LABELS = ["부정", "불만", "분노", "불안"]

# Potensdot 감성분석 API 사용

def potensdot_sentiment(text: str) -> str:
    api_key = os.environ.get("POTENSDOT_API_KEY")
    url = "https://ai.potens.ai/api/chat"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    prompt = f"아래 문장의 감정을 한 단어(긍정/부정/불만/분노/불안/중립 등)로만 답해줘.\n문장: {text}"
    data = {"prompt": prompt}
    resp = requests.post(url, headers=headers, json=data)
    if resp.status_code == 200:
        result = resp.json()
        answer = result.get("answer") or result.get("content") or str(result)
        return answer.strip().split()[0] if answer else ""
    else:
        return ""

def is_negative_sentiment_potensdot(text: str) -> bool:
    label = potensdot_sentiment(text)
    return label in NEGATIVE_LABELS 