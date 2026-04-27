import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.modules.intelligence.models import AIAgent, Suggestion
from app.modules.intelligence.schemas import (
    AIAgentCreate,
    AIAgentUpdate,
    SuggestionCreate,
    SuggestionUpdate,
)


# ── AI Agents ────────────────────────────────────────────
def get_all_agents(db: Session):
    return db.query(AIAgent).filter(AIAgent.deleted_at.is_(None)).all()


def get_agent_by_id(db: Session, agent_id: uuid.UUID) -> Optional[AIAgent]:
    return db.query(AIAgent).filter(AIAgent.id == agent_id, AIAgent.deleted_at.is_(None)).first()


def create_agent(db: Session, data: AIAgentCreate) -> AIAgent:
    agent = AIAgent(name=data.name, type=data.type, version=data.version)
    db.add(agent)
    db.commit()
    db.refresh(agent)
    return agent


def update_agent(db: Session, agent_id: uuid.UUID, data: AIAgentUpdate) -> Optional[AIAgent]:
    agent = get_agent_by_id(db, agent_id)
    if not agent:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(agent, field, value)
    db.commit()
    db.refresh(agent)
    return agent


def soft_delete_agent(db: Session, agent_id: uuid.UUID) -> Optional[AIAgent]:
    agent = get_agent_by_id(db, agent_id)
    if not agent:
        return None
    agent.deleted_at = datetime.now(timezone.utc)
    db.commit()
    return agent


# ── Suggestions ──────────────────────────────────────────
def get_suggestions_by_line(db: Session, line_id: uuid.UUID):
    return db.query(Suggestion).filter(
        Suggestion.production_line_id == line_id, Suggestion.deleted_at.is_(None)
    ).all()


def get_suggestion_by_id(db: Session, suggestion_id: uuid.UUID) -> Optional[Suggestion]:
    return db.query(Suggestion).filter(
        Suggestion.id == suggestion_id, Suggestion.deleted_at.is_(None)
    ).first()


def create_suggestion(db: Session, line_id: uuid.UUID, data: SuggestionCreate) -> Suggestion:
    suggestion = Suggestion(
        production_line_id=line_id,
        ai_agent_id=data.ai_agent_id,
        machine_id=data.machine_id,
        type=data.type,
        description=data.description,
        payload=data.payload,
        confidence=data.confidence,
    )
    db.add(suggestion)
    db.commit()
    db.refresh(suggestion)
    return suggestion


def update_suggestion(db: Session, suggestion_id: uuid.UUID, data: SuggestionUpdate) -> Optional[Suggestion]:
    suggestion = get_suggestion_by_id(db, suggestion_id)
    if not suggestion:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(suggestion, field, value)
    db.commit()
    db.refresh(suggestion)
    return suggestion
