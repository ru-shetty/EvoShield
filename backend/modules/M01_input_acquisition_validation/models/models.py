"""
Data models for EvoShield Module 1.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional


@dataclass
class Entity:
    """
    Represents an input entity processed by EvoShield.

    Module 1 creates this entity after identifying and validating
    the incoming input.
    """

    entity_id: str
    entity_type: str
    content: Any

    metadata: Dict[str, Any] = field(default_factory=dict)

    status: str = "QUEUED"

    routing_decision: Optional[str] = None

    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    updated_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    validation_errors: list = field(default_factory=list)

    def update_status(self, status: str) -> None:
        """
        Update processing status and timestamp.
        """
        self.status = status
        self.updated_at = datetime.now(timezone.utc)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert entity into a dictionary.
        """

        return {
            "entity_id": self.entity_id,
            "entity_type": self.entity_type,
            "content": self.content,
            "metadata": self.metadata,
            "status": self.status,
            "routing_decision": self.routing_decision,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "validation_errors": self.validation_errors,
        } 