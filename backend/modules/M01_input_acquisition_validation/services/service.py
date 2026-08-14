"""
Service layer for EvoShield Module 1.
"""

from typing import Any, Dict

from ..processors.processor import InputProcessor
from ..schemas.schemas import InputResponse


class InputAcquisitionService:
    """
    Business service for input acquisition and validation.
    """

    def __init__(self):
        self.processor = InputProcessor()

    def acquire(self, input_data: Any) -> InputResponse:
        """
        Acquire and process an incoming entity.
        """

        entity = self.processor.process(input_data)

        return InputResponse(
            entity_id=entity.entity_id,
            entity_type=entity.entity_type,
            status=entity.status,
            routing_decision=entity.routing_decision,
            metadata=entity.metadata,
            validation_errors=entity.validation_errors,
        )

    def acquire_from_request(
        self,
        request_data: Dict[str, Any],
    ) -> InputResponse:
        """
        Process structured request data.
        """

        if "data" not in request_data:
            raise ValueError(
                "Request must contain 'data'."
            )

        input_data = request_data["data"]

        return self.acquire(input_data)