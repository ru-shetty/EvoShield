"""
Serialization utilities for Module 1 API.
"""

from typing import Any, Dict

from ..schemas.schemas import InputResponse


def serialize_input_response(
    response: InputResponse,
) -> Dict[str, Any]:
    """
    Convert InputResponse into JSON-compatible dictionary.
    """

    return response.to_dict()


def validate_request_payload(
    payload: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Validate the basic API request structure.
    """

    if not isinstance(payload, dict):
        raise ValueError(
            "Request payload must be a JSON object."
        )

    if "data" not in payload:
        raise ValueError(
            "Missing required field: data"
        )

    return payload