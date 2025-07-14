"""
Hi-Care AI 챗봇 메인 애플리케이션 - 루트 진입점
uvicorn main:app 형태로 실행하기 위한 진입점
"""

from app.main import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)