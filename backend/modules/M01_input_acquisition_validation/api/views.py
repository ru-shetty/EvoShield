"""
API views for EvoShield Module 1.
"""

from typing import Any, Dict

from ..services.service import InputAcquisitionService
from .serializers import (
    serialize_input_response,
    validate_request_payload,
)


class InputAcquisitionView:
    """
    API view for Module 1.
    """

    def __init__(self):
        self.service = InputAcquisitionService()

    def post(
        self,
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Process an incoming input.
        """

        try:

            payload = validate_request_payload(payload)

            response = self.service.acquire(
                payload["data"]
            )

            return {
                "success": True,
                "data": serialize_input_response(
                    response
                ),
            }

        except Exception as exc:

            return {
                "success": False,
                "error": str(exc),
            }