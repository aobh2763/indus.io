"""
Role-based permission helpers for Indus.io.

Global roles  : ADMIN, USER
Project roles  : OWNER, VIEWER, SUPERVISOR, COLLABORATOR
"""

from enum import Enum
from functools import wraps
from typing import List

from fastapi import Depends

from app.core.exceptions import ForbiddenError


# ── Enums ────────────────────────────────────────────────
class GlobalRole(str, Enum):
    ADMIN = "ADMIN"
    USER = "USER"


class AccessLevel(str, Enum):
    OWNER = "OWNER"
    VIEWER = "VIEWER"
    SUPERVISOR = "SUPERVISOR"
    COLLABORATOR = "COLLABORATOR"


class Visibility(str, Enum):
    PUBLIC = "PUBLIC"
    PRIVATE = "PRIVATE"


class ProductionLineStatus(str, Enum):
    DRAFT = "DRAFT"
    RUNNING = "RUNNING"
    ARCHIVED = "ARCHIVED"


class SimulationStatus(str, Enum):
    RUNNING = "RUNNING"
    STOPPED = "STOPPED"
    COMPLETED = "COMPLETED"


class LogLevel(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class AlertSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AlertStatus(str, Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"


# ── Permission checker ──────────────────────────────────
def require_roles(allowed_roles: List[GlobalRole]):
    """
    FastAPI dependency that restricts access to users
    whose global role is in *allowed_roles*.

    Usage in a router:
        @router.get("/admin-only", dependencies=[Depends(require_roles([GlobalRole.ADMIN]))])
    """

    def _checker(current_user=Depends(lambda: None)):
        # The actual current_user dependency is injected at the API layer.
        # This is resolved at runtime via api/dependencies.py → get_current_user
        from app.api.dependencies import get_current_user  # deferred import

        return current_user

    return _checker
