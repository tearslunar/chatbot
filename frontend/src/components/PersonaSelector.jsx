import React, { useState, useEffect, useCallback } from 'react';
import './PersonaSelector.css';

const API_URL = import.meta.env.VITE_API_URL;

function PersonaSelector({ onPersonaSelect, selectedPersona }) {
  const [personas, setPersonas] = useState([]);
  const [searchKeyword, setSearchKeyword] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);

  const loadPersonas = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (searchKeyword) params.append('keyword', searchKeyword);
      params.append('limit', '20');
      
      const res = await fetch(`${API_URL}/persona-list?${params}`, {
        headers: {
          'ngrok-skip-browser-warning': 'true'
        }
      });
      if (res.ok) {
        const data = await res.json();
        setPersonas(data);
      }
    } catch (e) {
      console.error('페르소나 목록 로드 실패:', e);
    } finally {
      setLoading(false);
    }
  }, [searchKeyword]);

  // 페르소나 목록 로드
  useEffect(() => {
    loadPersonas();
  }, [loadPersonas]);

  const handlePersonaSelect = (persona) => {
    onPersonaSelect(persona);
    setIsOpen(false);
  };

  const clearPersona = () => {
    onPersonaSelect(null);
    setIsOpen(false);
  };

  return (
    <div className="persona-selector">
      <button 
        className="persona-selector-toggle"
        onClick={() => setIsOpen(!isOpen)}
      >
        👤 페르소나: {selectedPersona ? 
          `${selectedPersona.페르소나명} (${selectedPersona.연령대} ${selectedPersona.성별})` : 
          '선택 안함'
        }
        <span className="dropdown-arrow">{isOpen ? '▲' : '▼'}</span>
      </button>
      
      {isOpen && (
        <div className="persona-dropdown">
          <div className="persona-search">
            <input
              type="text"
              placeholder="페르소나 검색..."
              value={searchKeyword}
              onChange={(e) => setSearchKeyword(e.target.value)}
            />
          </div>
          
          <div className="persona-list">
            <div 
              className="persona-item clear-option" 
              onClick={clearPersona}
            >
              🚫 페르소나 선택 해제
            </div>
            
            {loading && <div className="persona-loading">로딩 중...</div>}
            
            {personas.map((persona) => (
              <div
                key={persona.ID}
                className="persona-item"
                onClick={() => handlePersonaSelect(persona)}
              >
                <div className="persona-basic">
                  <strong>{persona.페르소나명}</strong>
                  <span className="persona-job">{persona.연령대} {persona.성별}</span>
                </div>
                <div className="persona-details">
                  {persona.직업} | {persona.거주지} | {persona['가족 구성']}
                </div>
                <div className="persona-interests">
                  차량: {persona['차량 정보']}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default PersonaSelector; 