import React from 'react';
import { useChatContext } from '../context/ChatContext';

const MODEL_OPTIONS = [
  { label: 'Claude 3.7 sonnet', value: 'claude-3.7-sonnet' },
  { label: 'Claude 4.0 sonnet', value: 'claude-4.0-sonnet' },
  { label: 'Claude 3.5 Haiku', value: 'claude-3.5-haiku' },
  { label: 'Claude 3.7 Sonnet Extended Thinking', value: 'claude-3.7-sonnet-extended' },
];

const ModelSelector = () => {
  const { state, actions } = useChatContext();
  const { model } = state;

  return (
    <div className="model-select-row">
      <label htmlFor="model-select">모델 선택: </label>
      <select
        id="model-select"
        value={model}
        onChange={e => actions.setModel(e.target.value)}
      >
        {MODEL_OPTIONS.map(opt => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
    </div>
  );
};

export default ModelSelector;