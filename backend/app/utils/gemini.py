import os
import google.generativeai as genai

def get_gemini_answer(user_message: str, model_name: str) -> str:
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        return "(서버 설정 오류) GOOGLE_API_KEY가 등록되어 있지 않습니다."
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(user_message)
        return response.text.strip()
    except Exception as e:
        return f"(Gemini API 오류) {str(e)}" 