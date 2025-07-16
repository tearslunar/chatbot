import os
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import re
from difflib import SequenceMatcher

PERSONA_CSV_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', '..', 'data', 'customer_persona.csv')

class PersonaManager:
    def __init__(self, csv_path=PERSONA_CSV_PATH):
        try:
            # CSV 파일 수동 처리
            import csv
            data = []
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # ID가 'P'로 시작하는 올바른 행만 추가
                    if row.get('ID', '').startswith('P'):
                        data.append(row)
            
            self.df = pd.DataFrame(data)
            self.df.fillna('', inplace=True)
            
            print(f"페르소나 데이터 로드 완료: {len(self.df)}개 페르소나")
            # 헤더 확인
            print("CSV 헤더:", list(self.df.columns))
            # 첫 번째 행의 데이터 확인
            if len(self.df) > 0:
                first_row = dict(self.df.iloc[0])
                print("첫 번째 페르소나 샘플:")
                for key, value in first_row.items():
                    print(f"  {key}: {value}")
        except Exception as e:
            print(f"페르소나 CSV 파일 로드 실패: {e}")
            # 빈 DataFrame으로 초기화
            self.df = pd.DataFrame()

    def list_personas(self, keyword=None, limit=100):
        try:
            df = self.df
            if keyword:
                mask = df.apply(lambda row: keyword in str(row.values), axis=1)
                df = df[mask]
            return df.head(limit).to_dict(orient='records')
        except Exception as e:
            print(f"페르소나 목록 조회 오류: {e}")
            return []

    def get_persona_by_id(self, persona_id):
        row = self.df[self.df['ID'] == persona_id]
        if not row.empty:
            return row.iloc[0].to_dict()
        return None
    
    def match_persona(self, customer_info: Dict) -> Tuple[Dict, float]:
        """
        고객 정보를 기반으로 가장 적합한 페르소나를 매칭
        
        Args:
            customer_info: {
                'age': '20대',
                'gender': '남성',
                'job': 'IT 개발자',
                'location': '서울',
                'vehicle': '현대 아반떼',
                'driving_experience': '1년',
                'family': '1인 가구'
            }
        
        Returns:
            (matched_persona, confidence_score)
        """
        if self.df.empty:
            return {}, 0.0
        
        scores = []
        
        for _, persona in self.df.iterrows():
            score = 0.0
            total_weight = 0.0
            
            # 연령대 매칭 (가중치: 25%)
            if customer_info.get('age'):
                if customer_info['age'] == persona.get('연령대', ''):
                    score += 25
                total_weight += 25
            
            # 성별 매칭 (가중치: 15%)
            if customer_info.get('gender'):
                if customer_info['gender'] == persona.get('성별', ''):
                    score += 15
                total_weight += 15
            
            # 직업 매칭 (가중치: 20%)
            if customer_info.get('job'):
                job_similarity = self._calculate_text_similarity(
                    customer_info['job'], persona.get('직업', '')
                )
                score += 20 * job_similarity
                total_weight += 20
            
            # 거주지 매칭 (가중치: 10%)
            if customer_info.get('location'):
                location_similarity = self._calculate_text_similarity(
                    customer_info['location'], persona.get('거주지', '')
                )
                score += 10 * location_similarity
                total_weight += 10
            
            # 차량 정보 매칭 (가중치: 15%)
            if customer_info.get('vehicle'):
                vehicle_similarity = self._calculate_text_similarity(
                    customer_info['vehicle'], persona.get('차량 정보', '')
                )
                score += 15 * vehicle_similarity
                total_weight += 15
            
            # 가족 구성 매칭 (가중치: 15%)
            if customer_info.get('family'):
                family_similarity = self._calculate_text_similarity(
                    customer_info['family'], persona.get('가족 구성', '')
                )
                score += 15 * family_similarity
                total_weight += 15
            
            # 정규화된 점수 계산
            confidence = score / total_weight if total_weight > 0 else 0.0
            scores.append((persona.to_dict(), confidence))
        
        # 가장 높은 점수의 페르소나 반환
        if scores:
            best_match = max(scores, key=lambda x: x[1])
            return best_match
        
        return {}, 0.0
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """텍스트 유사도 계산"""
        if not text1 or not text2:
            return 0.0
        
        # 정규화
        text1 = text1.lower().strip()
        text2 = text2.lower().strip()
        
        # 완전 일치
        if text1 == text2:
            return 1.0
        
        # 부분 일치 검사
        if text1 in text2 or text2 in text1:
            return 0.8
        
        # 유사도 계산
        return SequenceMatcher(None, text1, text2).ratio()
    
    def get_renewal_candidates(self, days_ahead: int = 30) -> List[Dict]:
        """
        갱신 예정 고객 목록 조회
        
        Args:
            days_ahead: 앞으로 며칠 이내 갱신 예정인지
        
        Returns:
            갱신 예정 페르소나 리스트
        """
        if self.df.empty or '갱신시기' not in self.df.columns:
            return []
        
        today = datetime.now()
        target_date = today + timedelta(days=days_ahead)
        
        renewal_candidates = []
        
        for _, persona in self.df.iterrows():
            renewal_date_str = persona.get('갱신시기', '')
            if not renewal_date_str:
                continue
            
            try:
                renewal_date = datetime.strptime(renewal_date_str, '%Y-%m-%d')
                # 갱신일이 오늘부터 지정된 일수 이내인 경우
                if today <= renewal_date <= target_date:
                    persona_dict = persona.to_dict()
                    persona_dict['days_to_renewal'] = (renewal_date - today).days
                    renewal_candidates.append(persona_dict)
            except ValueError:
                continue
        
        # 갱신일이 가까운 순으로 정렬
        renewal_candidates.sort(key=lambda x: x['days_to_renewal'])
        return renewal_candidates
    
    def get_personalized_recommendations(self, persona: Dict) -> Dict:
        """
        페르소나 기반 맞춤 추천 정보 생성
        
        Args:
            persona: 페르소나 정보
        
        Returns:
            추천 정보 딕셔너리
        """
        recommendations = {
            'greeting_style': self._get_greeting_style(persona),
            'recommended_products': self._get_recommended_products(persona),
            'discount_options': self._get_discount_options(persona),
            'communication_tone': self._get_communication_tone(persona),
            'priority_concerns': self._get_priority_concerns(persona)
        }
        
        return recommendations
    
    def _get_greeting_style(self, persona: Dict) -> str:
        """페르소나별 인사 스타일"""
        age = persona.get('연령대', '')
        digital_usage = persona.get('디지털 활용도 (온라인 가입/앱 활용)', '')
        
        if '20대' in age and '매우 높음' in digital_usage:
            return 'casual_friendly'  # 친근한 톤
        elif '30대' in age and '자녀' in persona.get('가족 구성', ''):
            return 'professional_caring'  # 전문적이면서 세심한 톤
        elif '40대' in age:
            return 'respectful_professional'  # 정중하고 전문적인 톤
        else:
            return 'standard'  # 표준 톤
    
    def _get_recommended_products(self, persona: Dict) -> List[str]:
        """페르소나별 추천 상품"""
        recommendations = []
        
        # 현재 가입 상품 분석
        current_product = persona.get('현재 가입 상품 (현대해상)', '')
        
        # 가족 구성에 따른 추천
        family = persona.get('가족 구성', '')
        if '자녀' in family:
            recommendations.append('어린이보험')
            recommendations.append('자녀할인특약')
        
        # 건강 관심도에 따른 추천
        health_concern = persona.get('건강 상태 및 관심 질병 (현재/가족력/관심도)', '')
        if '높음' in health_concern:
            recommendations.append('실손의료보험')
            recommendations.append('암보험')
        
        # 차량 정보에 따른 추천
        vehicle = persona.get('차량 정보', '')
        if any(premium_brand in vehicle for premium_brand in ['BMW', '벤츠', 'LEXUS', '테슬라']):
            recommendations.append('프리미엄 자차보상')
        
        return recommendations[:3]  # 최대 3개까지
    
    def _get_discount_options(self, persona: Dict) -> List[str]:
        """페르소나별 할인 옵션 추천"""
        discounts = []
        
        # 현재 특약 분석
        current_discounts = persona.get('주요 특약 (현대해상 다이렉트 기준)', '')
        
        # 운전 패턴에 따른 할인
        driving_pattern = persona.get('주요 주행 패턴', '')
        if '출퇴근' in driving_pattern:
            discounts.append('마일리지할인')
        
        # 운전 습관에 따른 할인
        driving_habit = persona.get('운전 습관', '')
        if '안전' in driving_habit:
            discounts.append('안전운전할인(UBI)')
            discounts.append('텔레매틱스할인')
        
        # 디지털 활용도에 따른 할인
        digital_usage = persona.get('디지털 활용도 (온라인 가입/앱 활용)', '')
        if '높음' in digital_usage or '매우 높음' in digital_usage:
            discounts.append('다이렉트할인')
            discounts.append('모바일앱할인')
        
        return discounts
    
    def _get_communication_tone(self, persona: Dict) -> str:
        """페르소나별 커뮤니케이션 톤"""
        info_channel = persona.get('정보 탐색 채널', '')
        
        if 'SNS' in info_channel or '유튜브' in info_channel:
            return 'trendy_casual'
        elif '커뮤니티' in info_channel:
            return 'informative_detailed'
        elif '블로그' in info_channel:
            return 'explanatory_helpful'
        else:
            return 'professional_standard'
    
    def _get_priority_concerns(self, persona: Dict) -> List[str]:
        """페르소나별 우선 관심사"""
        concerns = []
        
        pain_points = persona.get('페인 포인트', '')
        core_needs = persona.get('핵심 니즈', '')
        
        # 페인 포인트에서 우선순위 추출
        if '보험료' in pain_points or '보험료' in core_needs:
            concerns.append('cost_optimization')
        
        if '사고' in pain_points or '불안' in pain_points:
            concerns.append('accident_support')
        
        if '복잡' in pain_points:
            concerns.append('simplified_process')
        
        if '자녀' in pain_points or '가족' in core_needs:
            concerns.append('family_protection')
        
        return concerns

    def get_greeting_message(self, persona: dict) -> str:
        """페르소나 정보를 바탕으로 맞춤형 인사말 생성"""
        이름 = persona.get('페르소나명', '고객')
        연령대 = persona.get('연령대', '')
        성별 = persona.get('성별', '')
        직업 = persona.get('직업', '')
        거주지 = persona.get('거주지', '')
        가족구성 = persona.get('가족 구성', '')
        차량정보 = persona.get('차량 정보', '')
        핵심니즈 = persona.get('핵심 니즈', '')
        가입상품 = persona.get('현재 가입 상품 (Hi-Care)', '')
        
        # 기본 인사말
        greeting = f"안녕하세요, {이름}님! 😊\n\n"
        
        # 연령대와 성별을 고려한 맞춤형 인사
        if '20대' in 연령대:
            greeting += "젊은 나이에 보험에 관심을 가지시다니 정말 현명하시네요! ☀️\n"
        elif '30대' in 연령대:
            greeting += "인생의 중요한 시기에 든든한 보장을 준비하시는군요! 👍\n"
        elif '40대' in 연령대:
            greeting += "가족과 미래를 위해 보험을 알아보시는 책임감이 대단하세요! 🏠\n"
        elif '50대' in 연령대:
            greeting += "인생의 안정과 노후 준비를 위해 찾아주셨네요! 🌟\n"
        elif '60대' in 연령대:
            greeting += "풍부한 경험과 지혜를 바탕으로 안전한 보장을 생각하시는군요! 👴\n"
        
        # 직업을 고려한 맞춤형 메시지
        if 'IT' in 직업 or '개발자' in 직업:
            greeting += "IT 분야에서 활약하시는 분이시군요. 바쁜 업무 중에도 보험 상담을 받으시려 하니 감사합니다.\n"
        elif '의사' in 직업:
            greeting += "의료진으로서 건강의 중요성을 잘 아시는 분이시네요. 더욱 안전한 보장을 위해 도와드리겠습니다.\n"
        elif '교사' in 직업 or '강사' in 직업:
            greeting += "교육 분야에서 활동하시는 분이시군요. 안정적인 보장을 위해 함께 알아보아요.\n"
        elif '주부' in 직업:
            greeting += "가정을 돌보시면서도 가족의 안전을 생각하시는 따뜻한 마음이 느껴져요.\n"
        elif '자영업' in 직업 or '대표' in 직업:
            greeting += "사업을 하시면서 위험 관리에 신경 쓰시는 모습이 인상적이네요.\n"
        elif '공무원' in 직업:
            greeting += "공직에서 봉사하시는 분이시군요. 안정적인 보장을 위해 도와드릴게요.\n"
        
        # 가족 구성을 고려한 맞춤형 메시지
        if '자녀' in 가족구성:
            greeting += "자녀가 있으시니 더욱 든든한 보장이 중요하시겠네요.\n"
        elif '1인 가구' in 가족구성:
            greeting += "1인 가구로서 스스로를 위한 보장을 생각하시는 모습이 좋으시네요.\n"
        elif '배우자' in 가족구성:
            greeting += "가족과 함께 하시는 만큼 안전한 보장이 더욱 중요하시겠어요.\n"
        
        # 차량 정보를 고려한 맞춤형 안내
        if '현대' in 차량정보:
            greeting += "현대 차량을 이용하고 계시는군요! Hi-Care와 더욱 잘 맞는 보장을 제공해드릴 수 있어요. 🚗\n"
        elif '기아' in 차량정보:
            greeting += "기아 차량을 이용하고 계시는군요! 안전한 운전을 위한 보장을 함께 준비해보아요. 🚗\n"
        elif '테슬라' in 차량정보 or '전기' in 차량정보:
            greeting += "전기차를 이용하시는군요! 친환경 운전을 위한 특별한 보장을 알려드릴게요. ⚡\n"
        elif '벤츠' in 차량정보 or 'BMW' in 차량정보 or '제네시스' in 차량정보:
            greeting += "프리미엄 차량을 이용하시는군요! 고급 차량에 맞는 완벽한 보장을 제공해드릴게요. 🏆\n"
        
        # 핵심 니즈를 고려한 맞춤형 안내
        if '보험료' in 핵심니즈:
            greeting += "합리적인 보험료에 관심이 많으시군요. 최적의 가격으로 든든한 보장을 제공해드릴게요! 💰\n"
        elif '안전' in 핵심니즈:
            greeting += "안전에 대한 관심이 높으시군요. 완벽한 보장으로 마음의 평안을 드리겠습니다! 🛡️\n"
        elif '편리' in 핵심니즈:
            greeting += "편리한 서비스를 원하시는군요. 간편하고 빠른 절차로 도와드리겠습니다! 📱\n"
        
        # 기존 가입 상품을 고려한 멘트
        if '자동차' in 가입상품:
            greeting += "이미 Hi-Care 자동차보험을 이용해주고 계시는군요! 감사합니다. 🚙\n"
        elif '건강' in 가입상품:
            greeting += "Hi-Care 건강보험 고객이시군요! 늘 건강한 일상을 응원하겠습니다. 💊\n"
        elif '생명' in 가입상품:
            greeting += "Hi-Care 생명보험으로 이미 든든한 준비를 하고 계시네요! 👨‍👩‍👧‍👦\n"
        
        # 마무리 멘트
        greeting += "\n어떤 것이 궁금하시거나 도움이 필요하시면 언제든 말씀해주세요! 햇살봇이 성심껏 도와드릴게요. ☀️"
        
        return greeting

persona_manager = PersonaManager() 