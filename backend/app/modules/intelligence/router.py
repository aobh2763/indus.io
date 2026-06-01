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
@router.get("/ai-agents/explain", response_model=str, tags=["AI Agents"])
def explain_warning(warning: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return service.explain(warning)

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
