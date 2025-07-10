import React from 'react';
import './PrivacyPolicyModal.css';

const PrivacyPolicyModal = ({ isOpen, onClose, policyType = 'privacy' }) => {
  if (!isOpen) return null;

  const policies = {
    privacy: {
      title: '개인정보 수집·이용 동의서',
      content: `
🔐 개인정보 처리방침

1. 개인정보의 수집 및 이용 목적
   - 보험계약의 체결, 유지, 관리
   - 보험금 지급 및 보상처리
   - 고객 상담 및 서비스 제공
   - 법령상 의무 이행

2. 수집하는 개인정보 항목
   ※ 필수항목: 이름, 생년월일, 성별, 연락처, 이메일, 주소
   ※ 선택항목: 직업, 특이사항

3. 개인정보의 보유 및 이용기간
   - 보험계약 종료 후 5년 (상법 규정)
   - 단, 법령에 별도 보존기간이 정해진 경우 해당 기간

4. 개인정보 보안조치
   ✅ AES-256bit 암호화 저장
   ✅ 접근권한 관리 및 감사로그
   ✅ 개인정보보호법 완전 준수
   ✅ 정기적 보안점검 실시

5. 개인정보 제3자 제공
   - 원칙적으로 동의 없이 제3자 제공 금지
   - 법령 규정 또는 수사기관 요청시에만 제공

6. 개인정보처리 위탁
   - IT시스템 운영: (주)현대정보기술
   - 보험금 지급 심사: (주)현대손해사정
   ※ 위탁업체에도 동일한 보안기준 적용

7. 정보주체의 권리
   ✓ 개인정보 열람권
   ✓ 개인정보 정정·삭제권  
   ✓ 개인정보 처리정지권
   ✓ 손해배상청구권

8. 개인정보보호 책임자
   - 성명: 김○○ (개인정보보호팀장)
   - 연락처: privacy@hyundai.com
   - 전화: 02-3702-6000

※ 본 동의를 거부할 권리가 있으나, 거부 시 보험계약 체결이 제한될 수 있습니다.
      `
    },
    terms: {
      title: '보험약관 및 상품설명서',
      content: `
📋 보험약관 주요내용

1. 보험계약의 성립
   - 청약서 제출 → 회사 승낙 → 계약 성립
   - 계약자의 고지의무 (중요사항 성실 고지)

2. 보험료 납입
   - 첫회보험료: 계약 성립일로부터 1개월 이내
   - 월납보험료: 매월 납입일에 자동이체

3. 보험금 지급사유
   - 자동차보험: 대인/대물 사고, 자차손해 등
   - 건강보험: 질병/상해로 인한 입원, 수술 등
   - 여행보험: 여행 중 발생한 각종 사고

4. 보험금을 지급하지 않는 사유
   ❌ 고의 또는 중대한 과실
   ❌ 음주/무면허 운전
   ❌ 기존 질병 미고지
   ❌ 전쟁, 내란, 테러 등

5. 보험계약의 해지
   - 계약자의 임의해지 가능
   - 보험료 미납시 자동해지
   - 중요사항 미고지시 회사 해지

6. 소멸시효
   - 보험금청구권: 3년
   - 보험료반환청구권: 3년

7. 분쟁해결 절차
   1) 보험회사 고객센터 상담
   2) 금융감독원 분쟁조정위원회
   3) 법원 소송

※ 자세한 내용은 약관 전문을 참조하시기 바랍니다.
      `
    },
    marketing: {
      title: '마케팅 정보 수신 동의',
      content: `
📢 마케팅 활용 동의서

1. 수집·이용 목적
   - 신상품 정보 안내
   - 이벤트 및 프로모션 정보 제공
   - 맞춤형 서비스 추천
   - 고객만족도 조사

2. 수집항목
   - 연락처 정보 (전화번호, 이메일)
   - 관심 보험상품 정보
   - 서비스 이용 패턴

3. 보유·이용기간
   - 동의철회시 또는 회원탈퇴시까지
   - 최대 3년 (정보통신망법 기준)

4. 수신 방법
   ✉️ 이메일
   📱 SMS/카카오톡
   📞 전화 상담

5. 동의 철회
   - 고객센터 전화: 1588-5656
   - 이메일: unsubscribe@hyundai.com
   - 홈페이지 마이페이지에서 직접 변경

※ 본 동의는 선택사항이며, 거부하셔도 보험서비스 이용에는 제한이 없습니다.
      `
    },
    thirdParty: {
      title: '제3자 정보제공 동의',
      content: `
🔗 개인정보 제3자 제공 동의

1. 제공받는 자
   - 보험개발원 (보험사기 방지)
   - 도로교통공단 (교통법규 위반이력)
   - 건강보험심사평가원 (의료정보)

2. 제공 목적
   - 보험사기 방지 및 적정보험료 산출
   - 위험도 평가 및 언더라이팅
   - 보험금 지급 심사

3. 제공 항목
   - 기본정보: 이름, 생년월일, 성별
   - 계약정보: 보험가입내역, 사고이력
   - 의료정보: 진료기록 (건강보험 한정)

4. 보유·이용기간
   - 제공 목적 달성시까지
   - 법령에 따른 보존기간

5. 동의 거부권 및 불이익
   - 동의를 거부할 수 있습니다
   - 거부시 보험가입이 제한될 수 있습니다
   - 부정확한 위험평가로 보험료가 높아질 수 있습니다

※ 제공받는 기관도 개인정보보호법에 따라 정보를 안전하게 관리합니다.
      `
    }
  };

  const currentPolicy = policies[policyType] || policies.privacy;

  return (
    <div className="privacy-modal-overlay" onClick={onClose}>
      <div className="privacy-modal-content" onClick={e => e.stopPropagation()}>
        <div className="privacy-modal-header">
          <h2>{currentPolicy.title}</h2>
          <button className="privacy-modal-close" onClick={onClose}>×</button>
        </div>
        
        <div className="privacy-modal-body">
          <div className="policy-content">
            <pre>{currentPolicy.content}</pre>
          </div>
        </div>
        
        <div className="privacy-modal-footer">
          <div className="security-notice">
            <span className="security-icon">🔐</span>
            <span>귀하의 개인정보는 최고 수준의 보안으로 보호됩니다</span>
          </div>
          <button className="btn-primary" onClick={onClose}>
            확인
          </button>
        </div>
      </div>
    </div>
  );
};

export default PrivacyPolicyModal; 