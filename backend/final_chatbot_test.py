#!/usr/bin/env python3
"""
간단한 챗봇 서버 종합 테스트
실제 API 호출을 통한 완전한 기능 검증
"""

import requests
import json
import time
from datetime import datetime

class ChatbotTester:
    def __init__(self, base_url="http://localhost:8890"):
        self.base_url = base_url
        self.session_id = f"test_{int(time.time())}"
        
    def test_health(self):
        """헬스체크 테스트"""
        print("🏥 헬스체크 테스트")
        print("-" * 30)
        
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 서버 상태: {data['status']}")
                print(f"⏰ 타임스탬프: {data['timestamp']}")
                return True
            else:
                print(f"❌ 헬스체크 실패: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 헬스체크 오류: {e}")
            return False
    
    def test_basic_chat(self):
        """기본 채팅 기능 테스트"""
        print("\n💬 기본 채팅 테스트")
        print("-" * 30)
        
        test_messages = [
            {"msg": "안녕하세요", "expected_emotion": "중립"},
            {"msg": "자동차보험 가입하고 싶어요", "expected_emotion": "중립"},
            {"msg": "보험료가 궁금해요", "expected_emotion": "중립"},
            {"msg": "사고가 났어요 도와주세요", "expected_emotion": "중립"},
            {"msg": "감사합니다", "expected_emotion": "긍정"}
        ]
        
        success_count = 0
        
        for i, test in enumerate(test_messages, 1):
            print(f"\n[테스트 {i}] {test['msg']}")
            
            try:
                response = requests.post(
                    f"{self.base_url}/chat",
                    json={
                        "message": test["msg"],
                        "model": "test-model",
                        "session_id": self.session_id
                    },
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    answer = data["answer"]
                    emotion = data["emotion"]
                    processing_time = data["processing_time"]
                    
                    print(f"🤖 응답: {answer[:100]}...")
                    print(f"😊 감정: {emotion['emotion']} (강도: {emotion['intensity']})")
                    print(f"⚡ 처리시간: {processing_time}초")
                    
                    # 기본 검증
                    if len(answer) > 10 and "햇살봇" in answer:
                        print("✅ 응답 품질: 양호")
                        success_count += 1
                    else:
                        print("⚠️ 응답 품질: 개선 필요")
                        
                else:
                    print(f"❌ 응답 실패: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ 요청 오류: {e}")
        
        success_rate = (success_count / len(test_messages)) * 100
        print(f"\n📊 기본 채팅 테스트 결과: {success_count}/{len(test_messages)} 성공 ({success_rate:.1f}%)")
        return success_count > 0
    
    def test_emotion_detection(self):
        """감정 분석 테스트"""
        print("\n😊 감정 분석 테스트")
        print("-" * 30)
        
        emotion_tests = [
            {"msg": "정말 화가 나요!", "expected": "분노"},
            {"msg": "걱정이 돼요", "expected": "불안"},
            {"msg": "정말 좋은 서비스네요", "expected": "긍정"},
            {"msg": "보험료 문의드립니다", "expected": "중립"}
        ]
        
        success_count = 0
        
        for test in emotion_tests:
            print(f"\n메시지: {test['msg']}")
            print(f"예상 감정: {test['expected']}")
            
            try:
                response = requests.post(
                    f"{self.base_url}/chat",
                    json={"message": test["msg"], "session_id": self.session_id},
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    detected_emotion = data["emotion"]["emotion"]
                    intensity = data["emotion"]["intensity"]
                    
                    print(f"감지된 감정: {detected_emotion} (강도: {intensity})")
                    
                    if detected_emotion == test["expected"]:
                        print("✅ 감정 분석 정확")
                        success_count += 1
                    else:
                        print("⚠️ 감정 분석 부정확")
                        
            except Exception as e:
                print(f"❌ 감정 분석 오류: {e}")
        
        accuracy = (success_count / len(emotion_tests)) * 100
        print(f"\n📊 감정 분석 정확도: {success_count}/{len(emotion_tests)} ({accuracy:.1f}%)")
        return success_count > 0
    
    def test_performance(self):
        """성능 테스트"""
        print("\n⚡ 성능 테스트")
        print("-" * 30)
        
        test_message = "자동차보험 상담받고 싶어요"
        response_times = []
        
        for i in range(5):
            print(f"테스트 {i+1}/5...", end=" ")
            
            try:
                start_time = time.time()
                response = requests.post(
                    f"{self.base_url}/chat",
                    json={"message": test_message, "session_id": self.session_id},
                    timeout=10
                )
                end_time = time.time()
                
                if response.status_code == 200:
                    response_time = end_time - start_time
                    response_times.append(response_time)
                    print(f"{response_time:.3f}초")
                else:
                    print("실패")
                    
            except Exception as e:
                print(f"오류: {e}")
        
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            min_time = min(response_times)
            max_time = max(response_times)
            
            print(f"\n📊 성능 결과:")
            print(f"  평균 응답시간: {avg_time:.3f}초")
            print(f"  최소 응답시간: {min_time:.3f}초")
            print(f"  최대 응답시간: {max_time:.3f}초")
            
            return avg_time < 1.0  # 1초 이내면 성공
        
        return False
    
    def test_api_endpoints(self):
        """API 엔드포인트 테스트"""
        print("\n🔌 API 엔드포인트 테스트")
        print("-" * 30)
        
        endpoints = [
            {"url": "/", "method": "GET"},
            {"url": "/health", "method": "GET"},
            {"url": "/test-chat", "method": "POST", "data": {"test": "hello"}}
        ]
        
        success_count = 0
        
        for endpoint in endpoints:
            url = f"{self.base_url}{endpoint['url']}"
            method = endpoint["method"]
            
            print(f"{method} {endpoint['url']}...", end=" ")
            
            try:
                if method == "GET":
                    response = requests.get(url, timeout=5)
                elif method == "POST":
                    response = requests.post(url, json=endpoint.get("data", {}), timeout=5)
                
                if response.status_code == 200:
                    print("✅ 성공")
                    success_count += 1
                else:
                    print(f"❌ 실패 ({response.status_code})")
                    
            except Exception as e:
                print(f"❌ 오류: {e}")
        
        return success_count == len(endpoints)
    
    def run_comprehensive_test(self):
        """종합 테스트 실행"""
        print("🚀 현대해상 AI 챗봇 종합 테스트")
        print("=" * 50)
        print(f"테스트 시작: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"서버 URL: {self.base_url}")
        print(f"세션 ID: {self.session_id}")
        
        tests = [
            ("헬스체크", self.test_health),
            ("API 엔드포인트", self.test_api_endpoints),
            ("기본 채팅", self.test_basic_chat),
            ("감정 분석", self.test_emotion_detection),
            ("성능", self.test_performance)
        ]
        
        results = []
        
        for test_name, test_func in tests:
            print(f"\n{'='*50}")
            try:
                success = test_func()
                results.append((test_name, success))
            except Exception as e:
                print(f"❌ {test_name} 테스트 중 오류: {e}")
                results.append((test_name, False))
        
        # 최종 결과
        print(f"\n{'='*50}")
        print("🏆 최종 테스트 결과")
        print("=" * 50)
        
        success_count = 0
        for test_name, success in results:
            status = "✅ 성공" if success else "❌ 실패"
            print(f"{test_name}: {status}")
            if success:
                success_count += 1
        
        overall_success = (success_count / len(results)) * 100
        print(f"\n📊 전체 성공률: {success_count}/{len(results)} ({overall_success:.1f}%)")
        
        if overall_success >= 80:
            print("🎉 챗봇이 성공적으로 작동합니다!")
        elif overall_success >= 60:
            print("⚠️ 챗봇이 대체로 작동하지만 개선이 필요합니다.")
        else:
            print("❌ 챗봇에 심각한 문제가 있습니다.")
        
        print(f"\n테스트 완료: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    tester = ChatbotTester()
    tester.run_comprehensive_test() 