"""
페르소나 관리 라우터
고객 페르소나 선택, 인사말 생성, 페르소나별 맞춤형 서비스 제공
"""


from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Dict, Optional, List
import logging

from ..database import get_db
from ..repositories.session_repository import SessionRepository
from ..utils.persona_utils import persona_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/persona", tags=["persona"])

session_repository = SessionRepository()

class SetPersonaRequest(BaseModel):
    session_id: str
    persona_id: str

@router.post("/set")
def set_persona(req: SetPersonaRequest, db: Session = Depends(get_db)):
    persona = persona_manager.get_persona_by_id(req.persona_id)
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")

    session = session_repository.get_by_session_id(db, session_id=req.session_id)
    if not session:
        session = session_repository.create(db, obj_in={
            "session_id": req.session_id,
            "status": "active",
            "persona_id": req.persona_id
        })
    else:
        session_repository.update(db, db_obj=session, obj_in={"persona_id": req.persona_id})

    return {"success": True, "persona": persona}

class GreetingRequest(BaseModel):
    session_id: str

@router.post("/greeting")
def get_greeting(req: GreetingRequest, db: Session = Depends(get_db)):
    session = session_repository.get_by_session_id(db, session_id=req.session_id)
    if not session or not session.persona_id:
        raise HTTPException(status_code=400, detail="Persona not set for this session")

    persona = persona_manager.get_persona_by_id(session.persona_id)
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")

    greeting = persona_manager.get_greeting_message(persona)
    return {"success": True, "greeting": greeting}

@router.get("/list")
def get_personas():
    return persona_manager.get_all_personas() 