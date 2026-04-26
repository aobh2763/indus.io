from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.core.exceptions import NotFoundError
from app.modules.identity.models import User
from app.modules.intelligence import service
from app.modules.intelligence.schemas import (
    AIAgentCreate,
    AIAgentResponse,
    AIAgentUpdate,
    SuggestionCreate,
    SuggestionResponse,
    SuggestionUpdate,
)

router = APIRouter()


# ── AI Agents ────────────────────────────────────────────
@router.get("/ai-agents", response_model=list[AIAgentResponse], tags=["AI Agents"])
def list_agents(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return service.get_all_agents(db)


@router.post("/ai-agents", response_model=AIAgentResponse, status_code=201, tags=["AI Agents"])
def create_agent(data: AIAgentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return service.create_agent(db, data)


@router.get("/ai-agents/{agent_id}", response_model=AIAgentResponse, tags=["AI Agents"])
def get_agent(agent_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    agent = service.get_agent_by_id(db, agent_id)
    if not agent:
        raise NotFoundError("AI Agent")
    return agent


@router.put("/ai-agents/{agent_id}", response_model=AIAgentResponse, tags=["AI Agents"])
def update_agent(
    agent_id: str,
    data: AIAgentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    agent = service.update_agent(db, agent_id, data)
    if not agent:
        raise NotFoundError("AI Agent")
    return agent


@router.delete("/ai-agents/{agent_id}", status_code=204, tags=["AI Agents"])
def delete_agent(agent_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    agent = service.soft_delete_agent(db, agent_id)
    if not agent:
        raise NotFoundError("AI Agent")


# ── Suggestions ──────────────────────────────────────────
@router.get("/lines/{line_id}/suggestions", response_model=list[SuggestionResponse], tags=["Suggestions"])
def list_suggestions(line_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return service.get_suggestions_by_line(db, line_id)


@router.post("/lines/{line_id}/suggestions", response_model=SuggestionResponse, status_code=201, tags=["Suggestions"])
def create_suggestion(
    line_id: str,
    data: SuggestionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return service.create_suggestion(db, line_id, data)


@router.get("/suggestions/{suggestion_id}", response_model=SuggestionResponse, tags=["Suggestions"])
def get_suggestion(suggestion_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    suggestion = service.get_suggestion_by_id(db, suggestion_id)
    if not suggestion:
        raise NotFoundError("Suggestion")
    return suggestion


@router.put("/suggestions/{suggestion_id}", response_model=SuggestionResponse, tags=["Suggestions"])
def update_suggestion(
    suggestion_id: str,
    data: SuggestionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    suggestion = service.update_suggestion(db, suggestion_id, data)
    if not suggestion:
        raise NotFoundError("Suggestion")
    return suggestion
