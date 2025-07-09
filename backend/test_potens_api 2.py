#!/usr/bin/env python3
"""
포텐스닷 API 테스트 스크립트
현대해상 AI 챗봇 백엔드 - 포텐스닷 API 연결 상태 확인
"""

import os
import sys
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

class PotensAPITester:
    def __init__(self):
        self.api_key = os.environ.get("POTENSDOT_API_KEY")
        self.base_url = "https://ai.potens.ai/api/chat"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
    def print_header(self, title):
        """테스트 섹션 헤더 출력"""
        print(f"\n{'='*60}")
        print(f"  {title}")
        print(f"{'='*60}")
        
    def print_result(self, success, message, details=None):
        """테스트 결과 출력"""
        status = "✅ 성공" if success else "❌ 실패"
        print(f"{status}: {message}")
        if details:
            print(f"   상세: {details}")
            
    def test_api_key(self):
        """API 키 설정 확인"""
        self.print_header("API 키 설정 확인")
        
        if not self.api_key:
            self.print_result(False, "POTENSDOT_API_KEY 환경변수가 설정되지 않았습니다.")
            return False
            
        if len(self.api_key) < 20:
            self.print_result(False, "API 키가 너무 짧습니다. 올바른 키인지 확인해주세요.")
            return False
            
        self.print_result(True, f"API 키가 설정되었습니다. (길이: {len(self.api_key)})")
        return True
        
    def test_basic_connection(self):
        """기본 연결 테스트"""
        self.print_header("기본 연결 테스트")
        
        test_prompt = "안녕하세요"
        data = {"prompt": test_prompt}
        
        try:
            response = requests.post(
                self.base_url, 
                headers=self.headers, 
                json=data, 
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                self.print_result(True, "API 연결 성공")
                print(f"   응답 키: {list(result.keys())}")
                
                # 응답 내용 확인
                content = result.get("message") or result.get("content") or str(result)
                print(f"   응답 내용: {content[:100]}...")
                return True
            else:
                self.print_result(False, f"API 호출 실패 (상태코드: {response.status_code})")
                print(f"   응답 내용: {response.text[:200]}...")
                return False
                
        except requests.exceptions.Timeout:
            self.print_result(False, "API 응답 시간 초과 (10초)")
            return False
        except requests.exceptions.ConnectionError:
            self.print_result(False, "네트워크 연결 실패")
            return False
        except Exception as e:
            self.print_result(False, f"예외 발생: {str(e)}")
            return False
            
    def test_emotion_analysis(self):
        """감정 분석 테스트"""
        self.print_header("감정 분석 테스트")
        
        test_cases = [
            ("기쁘다", "긍정"),
            ("화가 난다", "부정"),
            ("짜증난다", "불만"),
            ("불안하다", "불안"),
            ("좋다", "긍정")
        ]
        
        success_count = 0
        
        for text, expected_emotion in test_cases:
            prompt = f"아래 문장의 감정을 한 단어(긍정/부정/불만/분노/불안/중립 등)로만 답해줘.\n문장: {text}"
            data = {"prompt": prompt}
            
            try:
                response = requests.post(
                    self.base_url, 
                    headers=self.headers, 
                    json=data, 
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    answer = result.get("message") or result.get("content") or str(result)
                    detected_emotion = answer.strip().split()[0] if answer else ""
                    
                    print(f"   '{text}' → '{detected_emotion}'")
                    success_count += 1
                else:
                    print(f"   '{text}' → 실패 (상태코드: {response.status_code})")
                    
            except Exception as e:
                print(f"   '{text}' → 예외: {str(e)}")
        
        success_rate = (success_count / len(test_cases)) * 100
        self.print_result(success_count == len(test_cases), 
                         f"감정 분석 테스트 ({success_count}/{len(test_cases)} 성공, {success_rate:.1f}%)")
        
        return success_count > 0
        
    def test_chat_response(self):
        """채팅 응답 테스트"""
        self.print_header("채팅 응답 테스트")
        
        test_questions = [
            "안녕하세요",
            "보험 상품에 대해 알려주세요",
            "자동차 보험 가입하고 싶어요",
            "사고 났을 때 어떻게 해야 하나요?"
        ]
        
        success_count = 0
        
        for question in test_questions:
            prompt = f"현대해상 고객상담 챗봇으로서 다음 질문에 답해주세요: {question}"
            data = {"prompt": prompt}
            
            try:
                response = requests.post(
                    self.base_url, 
                    headers=self.headers, 
                    json=data, 
                    timeout=15
                )
                
                if response.status_code == 200:
                    result = response.json()
                    answer = result.get("message") or result.get("content") or str(result)
                    
                    if answer and len(answer.strip()) > 10:
                        print(f"   Q: {question}")
                        print(f"   A: {answer[:100]}...")
                        success_count += 1
                    else:
                        print(f"   Q: {question}")
                        print(f"   A: 응답이 너무 짧습니다.")
                else:
                    print(f"   Q: {question}")
                    print(f"   A: 실패 (상태코드: {response.status_code})")
                    
            except Exception as e:
                print(f"   Q: {question}")
                print(f"   A: 예외 발생: {str(e)}")
        
        success_rate = (success_count / len(test_questions)) * 100
        self.print_result(success_count == len(test_questions), 
                         f"채팅 응답 테스트 ({success_count}/{len(test_questions)} 성공, {success_rate:.1f}%)")
        
        return success_count > 0
        
    def test_response_time(self):
        """응답 시간 테스트"""
        self.print_header("응답 시간 테스트")
        
        test_prompt = "안녕하세요"
        data = {"prompt": test_prompt}
        response_times = []
        
        for i in range(3):
            try:
                start_time = datetime.now()
                response = requests.post(
                    self.base_url, 
                    headers=self.headers, 
                    json=data, 
                    timeout=30
                )
                end_time = datetime.now()
                
                if response.status_code == 200:
                    response_time = (end_time - start_time).total_seconds()
                    response_times.append(response_time)
                    print(f"   테스트 {i+1}: {response_time:.2f}초")
                else:
                    print(f"   테스트 {i+1}: 실패 (상태코드: {response.status_code})")
                    
            except Exception as e:
                print(f"   테스트 {i+1}: 예외 발생: {str(e)}")
        
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            max_time = max(response_times)
            min_time = min(response_times)
            
            print(f"   평균 응답시간: {avg_time:.2f}초")
            print(f"   최대 응답시간: {max_time:.2f}초")
            print(f"   최소 응답시간: {min_time:.2f}초")
            
            # 5초 이내면 양호
            self.print_result(avg_time <= 5.0, f"응답 시간 테스트 (평균: {avg_time:.2f}초)")
            return avg_time <= 5.0
        else:
            self.print_result(False, "응답 시간 측정 실패")
            return False
            
    def run_all_tests(self):
        """모든 테스트 실행"""
        print("포텐스닷 API 테스트 시작")
        print(f"테스트 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        results = []
        
        # 1. API 키 확인
        results.append(self.test_api_key())
        
        if not results[0]:
            print("\n❌ API 키 설정 문제로 인해 테스트를 중단합니다.")
            return False
            
        # 2. 기본 연결 테스트
        results.append(self.test_basic_connection())
        
        if not results[1]:
            print("\n❌ 기본 연결 실패로 인해 추가 테스트를 건너뜁니다.")
            return False
            
        # 3. 감정 분석 테스트
        results.append(self.test_emotion_analysis())
        
        # 4. 채팅 응답 테스트
        results.append(self.test_chat_response())
        
        # 5. 응답 시간 테스트
        results.append(self.test_response_time())
        
        # 결과 요약
        self.print_header("테스트 결과 요약")
        
        test_names = ["API 키 설정", "기본 연결", "감정 분석", "채팅 응답", "응답 시간"]
        success_count = sum(results)
        
        for i, (name, result) in enumerate(zip(test_names, results)):
            status = "✅" if result else "❌"
            print(f"{status} {name}")
            
        print(f"\n총 {success_count}/{len(results)} 테스트 통과 ({success_count/len(results)*100:.1f}%)")
        
        if success_count == len(results):
            print("\n🎉 모든 테스트가 성공했습니다! 포텐스닷 API가 정상적으로 작동합니다.")
            return True
        elif success_count >= len(results) * 0.8:
            print("\n⚠️ 대부분의 테스트가 성공했지만, 일부 기능에 문제가 있을 수 있습니다.")
            return True
        else:
            print("\n❌ 테스트 실패가 많습니다. API 설정이나 네트워크 상태를 확인해주세요.")
            return False

def main():
    """메인 함수"""
    tester = PotensAPITester()
    
    try:
        success = tester.run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️ 테스트가 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류가 발생했습니다: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 