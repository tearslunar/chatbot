import React from 'react';
import { useChatContext } from '../context/ChatContext';

const ModalManager = () => {
  const { state, actions } = useChatContext();
  const { 
    isModalOpen, 
    isFeedbackModalOpen, 
    showInactivityWarning,
    remainingTime,
    rating,
    hoveredRating,
    feedback,
    sessionId
  } = state;

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  // 상담 종료 확인
  const handleEndChatConfirm = async () => {
    actions.setSessionEnded(true);
    actions.setModalOpen(false);
    actions.setFeedbackModalOpen(true);
    actions.addMessage({ 
      role: 'bot', 
      content: '상담이 종료되었습니다. 언제든 다시 찾아주세요 ☀️' 
    });

    // 상담 종료 API 호출
    try {
      const res = await fetch(`${API_URL}/chat/end-session`, { method: 'POST' });
      if (res.ok) {
        const data = await res.json();
        actions.setResolutionResult(data);
        console.log('해소 분석 결과:', data);
      }
    } catch (e) {
      console.warn('해소 분석 API 호출 실패:', e);
    }
  };

  // 피드백 제출
  const handleFeedbackSubmit = async () => {
    console.log('상담 종료 피드백:', feedback);
    console.log('상담 평점:', rating);
    
    try {
      const res = await fetch(`${API_URL}/chat/submit-rating`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'ngrok-skip-browser-warning': 'true'
        },
        body: JSON.stringify({
          session_id: sessionId,
          rating: rating,
          feedback: feedback,
          timestamp: new Date().toISOString()
        })
      });
      
      if (res.ok) {
        console.log('평점 제출 성공');
        actions.addMessage({ 
          role: 'bot', 
          content: '소중한 평가를 해주셔서 감사합니다! 더 나은 서비스로 보답하겠습니다. 😊' 
        });
      } else {
        console.warn('평점 제출 실패:', res.status);
      }
    } catch (e) {
      console.warn('평점 제출 API 호출 실패:', e);
    }
    
    actions.resetFeedback();
  };

  // 비활성 타이머 종료 처리
  const handleInactivityTimeout = () => {
    console.log('[비활성 타이머] 3분 경과로 상담을 자동 종료합니다.');
    actions.setSessionEnded(true);
    actions.setCurrentEmotion(null);
    actions.addMessage({ 
      role: 'bot', 
      content: '⏰ **3분간 대화가 없어 상담이 자동으로 종료되었습니다.** 서비스 이용 후기를 남겨주시면 더 나은 서비스 제공에 도움이 됩니다.' 
    });
    actions.setInactivityWarning(false);
    actions.setRemainingTime(0);
    
    // 자동 종료 후 바로 평점 입력창 표시
    setTimeout(() => {
      actions.setFeedbackModalOpen(true);
    }, 1000);
  };

  return (
    <>
      {/* 상담 종료 확인 모달 */}
      {isModalOpen && (
        <div className="modal-background">
          <div className="modal-content">
            <div className="modal-text">상담을 종료하겠습니까?</div>
            <p>어려움을 겪고 계신가요?<br />상담원이 도와드리겠습니다.<br />0000-0000</p>
            <div className="modal-buttons">
              <button className="modal-button yes" onClick={handleEndChatConfirm}>
                네
              </button>
              <button className="modal-button no" onClick={() => actions.setModalOpen(false)}>
                아니오
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 피드백 입력 모달 */}
      {isFeedbackModalOpen && (
        <div className="modal-background">
          <div className="modal-content" style={{ 
            minWidth: 380, 
            maxWidth: 450, 
            display: 'flex', 
            flexDirection: 'column', 
            justifyContent: 'center', 
            alignItems: 'center', 
            minHeight: 280 
          }}>
            <div className="modal-text" style={{ 
              color: '#d2691e', 
              marginBottom: 20, 
              fontSize: '18px', 
              fontWeight: 'bold' 
            }}>
              상담은 어떠셨나요?
            </div>
            
            {/* 별점 입력 섹션 */}
            <div style={{ marginBottom: 20 }}>
              <div style={{ 
                textAlign: 'center', 
                marginBottom: 12, 
                fontSize: '14px', 
                color: '#666' 
              }}>
                서비스 만족도를 평가해주세요
              </div>
              <div style={{ display: 'flex', gap: '8px', justifyContent: 'center' }}>
                {[1, 2, 3, 4, 5].map((star) => (
                  <button
                    key={star}
                    style={{
                      background: 'none',
                      border: 'none',
                      fontSize: '36px',
                      cursor: 'pointer',
                      color: (hoveredRating >= star || rating >= star) ? '#ffc107' : '#e0e0e0',
                      transition: 'color 0.2s ease',
                      padding: '4px'
                    }}
                    onMouseEnter={() => actions.setHoveredRating(star)}
                    onMouseLeave={() => actions.setHoveredRating(0)}
                    onClick={() => actions.setRating(star)}
                  >
                    ★
                  </button>
                ))}
              </div>
              {rating > 0 && (
                <div style={{ 
                  textAlign: 'center', 
                  marginTop: '8px', 
                  fontSize: '14px', 
                  color: '#666' 
                }}>
                  {rating === 1 && '매우 불만족'}
                  {rating === 2 && '불만족'}
                  {rating === 3 && '보통'}
                  {rating === 4 && '만족'}
                  {rating === 5 && '매우 만족'}
                </div>
              )}
            </div>

            {/* 텍스트 피드백 입력 */}
            <textarea
              value={feedback}
              onChange={e => actions.setFeedback(e.target.value)}
              placeholder="개선점이나 의견을 자유롭게 입력해 주세요 (선택사항)"
              rows={4}
              style={{ 
                width: '100%', 
                minHeight: 80, 
                marginBottom: 24, 
                borderRadius: 8, 
                border: '1px solid #ddd', 
                padding: 12, 
                fontSize: 15, 
                background: '#fafafa', 
                color: '#222', 
                resize: 'none' 
              }}
            />
            
            <div className="modal-buttons" style={{ justifyContent: 'center', width: '100%' }}>
              <button 
                className="modal-button yes" 
                onClick={handleFeedbackSubmit}
                disabled={rating === 0}
                style={{ 
                  opacity: rating === 0 ? 0.5 : 1,
                  cursor: rating === 0 ? 'not-allowed' : 'pointer'
                }}
              >
                제출하기
              </button>
              <button className="modal-button no" onClick={() => actions.resetFeedback()}>
                건너뛰기
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 비활성 경고 모달 */}
      {showInactivityWarning && (
        <div className="modal-background">
          <div className="modal-content" style={{ 
            minWidth: 320, 
            maxWidth: 400, 
            display: 'flex', 
            flexDirection: 'column', 
            justifyContent: 'center', 
            alignItems: 'center', 
            minHeight: 200, 
            background: '#fff3cd', 
            border: '2px solid #ffc107' 
          }}>
            <div style={{ fontSize: '48px', marginBottom: 16 }}>⏰</div>
            <div className="modal-text" style={{ 
              color: '#856404', 
              marginBottom: 16, 
              textAlign: 'center', 
              fontWeight: 'bold' 
            }}>
              비활성 상태 감지
            </div>
            <div style={{ 
              color: '#856404', 
              marginBottom: 20, 
              textAlign: 'center', 
              lineHeight: 1.5 
            }}>
              {remainingTime}초 후 상담이 자동으로 종료됩니다.<br/>
              메시지를 입력하시면 상담이 계속됩니다.
            </div>
            <div className="modal-buttons" style={{ justifyContent: 'center', width: '100%' }}>
              <button 
                className="modal-button yes" 
                onClick={() => {
                  actions.updateActivityTime();
                }}
                style={{ background: '#ffc107', border: 'none', color: '#000' }}
              >
                상담 계속하기
              </button>
              <button 
                className="modal-button no" 
                onClick={handleInactivityTimeout}
              >
                상담 종료
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default ModalManager;