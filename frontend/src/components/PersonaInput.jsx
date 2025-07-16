import React, { useState } from "react";
import { useChatContext } from '../context/ChatContext';
import './PersonaInput.css';

const PersonaInput = () => {
  const { state, actions } = useChatContext();

  const [formData, setFormData] = useState({
    name: '',
    age: '',
    gender: '',
    married: false,
    children: '',
    job: '',
    education: '',
    insurance: [],
    lifeStage: '',
    riskTolerance: 2
  });

  const handleChange = (e) => {
    const { name, type, value, checked, options } = e.target;

    if (type === 'checkbox') {
      setFormData(prev => ({ ...prev, [name]: checked }));
    } else if (type === 'select-multiple') {
      const selectedOptions = Array.from(options)
        .filter(option => option.selected)
        .map(option => option.value);
      setFormData(prev => ({ ...prev, [name]: selectedOptions }));
    } else if (type === 'range' || type === 'number') {
      setFormData(prev => ({ ...prev, [name]: Number(value) }));
    } else {
      setFormData(prev => ({ ...prev, [name]: value }));
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log("페르소나 JSON:", JSON.stringify(formData, null, 2));
    // actions.setPersona(formData) 등으로 저장할 수도 있음
  };

  return (
    <>
      {state.DevMode && (
        <div className="PersonaInput">
          <div>페르소나 입력창</div>
          <br />
          <form onSubmit={handleSubmit}>
            <ul className="PersonaData">
              <li><label>고객 이름 : <input type="text" name="name" value={formData.name} onChange={handleChange} /></label></li>
              <li><label>나이 : <input type="number" name="age" value={formData.age} onChange={handleChange} /></label></li>
              <li><label>성별 : <input type="text" name="gender" value={formData.gender} onChange={handleChange} /></label></li>
              <li><label>결혼 상태 : <input type="checkbox" name="married" checked={formData.married} onChange={handleChange} /></label></li>
              <li><label>자녀들의 수 : <input type="number" name="children" value={formData.children} onChange={handleChange} /></label></li>
              <li><label>직업 : <input type="text" name="job" value={formData.job} onChange={handleChange} /></label></li>
              <li>
                <label>교육 수준 :
                  <select name="education" value={formData.education} onChange={handleChange}>
                    <option value="" disabled hidden>선택하세요</option>
                    <option>고졸</option>
                    <option>대졸</option>
                    <option>대학원졸</option>
                    <option>전문직</option>
                  </select>
                </label>
              </li>
              <li>
                <label>기존 보험 :
                  <select multiple size="6" name="insurance" value={formData.insurance} onChange={handleChange}>
                    <option>자동차보험</option>
                    <option>건강보험</option>
                    <option>생명보험</option>
                    <option>상해보험</option>
                    <option>여행보험</option>
                    <option>재산보험</option>
                  </select>
                </label>
              </li>
              <li>
                <label>인생 단계 :
                  <select name="lifeStage" value={formData.lifeStage} onChange={handleChange}>
                    <option value="" disabled hidden>선택하세요</option>
                    <option>청년 독신</option>
                    <option>신혼기</option>
                    <option>자녀 양육기</option>
                    <option>중년기</option>
                    <option>은퇴준비기</option>
                    <option>은퇴기</option>
                  </select>
                </label>
              </li>
              <li><label>리스크 감내성 : <input type="range" min="1" max="3" name="riskTolerance" value={formData.riskTolerance} onChange={handleChange} /></label></li>
              <br />
            </ul>
            <div className="form_btn">
              <button type="submit" className="submit_btn">등록</button>
              <button type="reset" className="reset_btn" onClick={() => setFormData({
                name: '',
                age: '',
                gender: '',
                married: false,
                children: '',
                job: '',
                education: '',
                insurance: [],
                lifeStage: '',
                riskTolerance: 2
              })}>리셋</button>
            </div>
          </form>
        </div>
      )}
    </>
  );
};
export default PersonaInput;
/*
age: int
gender: str
marital_status: str
children_count: int
occupation: str
income_level: str
education_level: EducationLevel
life_stage: LifeStage
existing_insurance: List[str]
risk_tolerance: str  # low, medium, high
*/ 