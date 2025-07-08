import React from 'react';
import './SuggestedQuestions.css';

function SuggestedQuestions({ questions, onSelect }) {
  if (!questions || questions.length === 0) return null;
  return (
    <div className="suggested-questions-container">
      <ul className="suggested-questions-list">
        {questions.map((q, idx) => (
          <li key={idx} className="suggested-question-item" onClick={() => onSelect(q)}>
            {q}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default SuggestedQuestions; 