"""
Input processing logic for EvoShield Module 1.
"""

import mimetypes
import re
import uuid
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.parse import urlparse

from ..config import (
    MAX_TEXT_LENGTH,
    MAX_URL_LENGTH,
    ROUTES,
    STATUS_FAILED,
    STATUS_QUEUED,
    SUPPORTED_INPUT_TYPES,
)
from ..models.models import Entity


class InputProcessor:
    """
    Responsible for identifying, validating and routing inputs.
    """

    def __init__(self):
        self.supported_types = SUPPORTED_INPUT_TYPES
        self.routes = ROUTES

    # ---------------------------------------------------------
    # ENTITY ID
    # ---------------------------------------------------------

    def create_entity_id(self) -> str:
        """
        Create a unique EntityID.

        Example:
        ENT-9c2b3e4f...
        """

        return f"ENT-{uuid.uuid4().hex}"

    # ---------------------------------------------------------
    # INPUT TYPE IDENTIFICATION
    # ---------------------------------------------------------

    def identify_input_type(self, input_data: Any) -> str:
        """
        Identify the type of incoming input.

        Supported:
        URL, text, image, audio, video and file.
        """

        if isinstance(input_data, str):

            # Check whether the string is a URL
            if self._looks_like_url(input_data):
                return "url"

            # Otherwise treat it as text
            return "text"

        # Path-like input
        if isinstance(input_data, Path):
            return self.identify_file_type(input_data)

        # Dictionary input may contain explicit type
        if isinstance(input_data, dict):

            declared_type = input_data.get("type")

            if declared_type:
                declared_type = declared_type.lower().strip()

                if declared_type in self.supported_types:
                    return declared_type

        raise ValueError("Unable to identify input type.")

    # ---------------------------------------------------------
    # URL DETECTION
    # ---------------------------------------------------------

    def _looks_like_url(self, value: str) -> bool:
        """
        Determine whether a string looks like a URL.
        """

        value = value.strip()

        if not value:
            return False

        try:
            parsed = urlparse(value)

            return (
                parsed.scheme.lower() in {"http", "https"}
                and bool(parsed.netloc)
            )

        except Exception:
            return False

    # ---------------------------------------------------------
    # FILE TYPE IDENTIFICATION
    # ---------------------------------------------------------

    def identify_file_type(self, file_path: Path) -> str:
        """
        Identify whether a file is an image, audio, video or generic file.
        """

        if not file_path.exists():
            raise FileNotFoundError(
                f"Input file does not exist: {file_path}"
            )

        mime_type, _ = mimetypes.guess_type(str(file_path))

        if mime_type:

            if mime_type.startswith("image/"):
                return "image"

            if mime_type.startswith("audio/"):
                return "audio"

            if mime_type.startswith("video/"):
                return "video"

        return "file"

    # ---------------------------------------------------------
    # URL VALIDATION
    # ---------------------------------------------------------

    def validate_url(self, url: str) -> Dict[str, Any]:
        """
        Validate URL input.

        Module 2 will later perform malicious URL analysis.
        Module 1 only validates that the input is a usable URL.
        """

        errors = []

        if not isinstance(url, str):
            errors.append("URL must be a string.")
            return {
                "valid": False,
                "errors": errors,
            }

        url = url.strip()

        if not url:
            errors.append("URL cannot be empty.")

        if len(url) > MAX_URL_LENGTH:
            errors.append(
                f"URL exceeds maximum length of {MAX_URL_LENGTH}."
            )

        try:
            parsed = urlparse(url)

            if parsed.scheme.lower() not in {"http", "https"}:
                errors.append(
                    "URL must use HTTP or HTTPS."
                )

            if not parsed.netloc:
                errors.append(
                    "URL must contain a valid domain."
                )

        except Exception:
            errors.append("Invalid URL format.")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
        }

    # ---------------------------------------------------------
    # TEXT VALIDATION
    # ---------------------------------------------------------

    def validate_text(self, text: str) -> Dict[str, Any]:
        """
        Validate textual input.
        """

        errors = []

        if not isinstance(text, str):
            errors.append("Text must be a string.")
            return {
                "valid": False,
                "errors": errors,
            }

        if not text.strip():
            errors.append("Text cannot be empty.")

        if len(text) > MAX_TEXT_LENGTH:
            errors.append(
                f"Text exceeds maximum length of {MAX_TEXT_LENGTH}."
            )

        return {
            "valid": len(errors) == 0,
            "errors": errors,
        }

    # ---------------------------------------------------------
    # FILE VALIDATION
    # ---------------------------------------------------------

    def validate_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Validate a file path.
        """

        errors = []

        if not file_path.exists():
            errors.append("File does not exist.")

        if not file_path.is_file():
            errors.append("Input path is not a file.")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
        }

    # ---------------------------------------------------------
    # GENERAL VALIDATION
    # ---------------------------------------------------------

    def validate_input(
        self,
        input_data: Any,
        input_type: str,
    ) -> Dict[str, Any]:
        """
        Validate input according to its identified type.
        """

        input_type = input_type.lower().strip()

        if input_type == "url":
            return self.validate_url(input_data)

        if input_type == "text":
            return self.validate_text(input_data)

        if input_type in {"image", "audio", "video", "file"}:

            if isinstance(input_data, Path):
                return self.validate_file(input_data)

            if isinstance(input_data, str):
                return self.validate_file(Path(input_data))

            return {
                "valid": False,
                "errors": ["Invalid file input."],
            }

        return {
            "valid": False,
            "errors": [
                f"Unsupported input type: {input_type}"
            ],
        }

    # ---------------------------------------------------------
    # METADATA
    # ---------------------------------------------------------

    def create_metadata(
        self,
        input_data: Any,
        input_type: str,
    ) -> Dict[str, Any]:
        """
        Create metadata associated with the input.
        """

        metadata = {
            "input_type": input_type,
        }

        if isinstance(input_data, str):

            metadata["input_length"] = len(input_data)

        elif isinstance(input_data, Path):

            metadata["file_name"] = input_data.name
            metadata["file_extension"] = input_data.suffix.lower()

            try:
                metadata["file_size"] = input_data.stat().st_size
            except OSError:
                metadata["file_size"] = None

        elif isinstance(input_data, dict):

            metadata.update(
                input_data.get("metadata", {})
            )

        return metadata

    # ---------------------------------------------------------
    # ROUTING
    # ---------------------------------------------------------

    def route_input(self, input_type: str) -> str:
        """
        Determine which domain analyzer should receive the entity.
        """

        input_type = input_type.lower().strip()

        if input_type not in self.routes:
            raise ValueError(
                f"No route available for input type: {input_type}"
            )

        return self.routes[input_type]

    # ---------------------------------------------------------
    # MAIN PROCESS
    # ---------------------------------------------------------

    def process(self, input_data: Any) -> Entity:
        """
        Main Module 1 processing pipeline.

        Steps:
        1. Identify input type
        2. Validate input
        3. Create EntityID
        4. Attach metadata
        5. Route to analyzer
        6. Set status
        """

        entity_id = self.create_entity_id()

        try:

            # Step 1: Identify input
            input_type = self.identify_input_type(input_data)

            # Step 2: Validate input
            validation = self.validate_input(
                input_data,
                input_type,
            )

            # Step 3: Create metadata
            metadata = self.create_metadata(
                input_data,
                input_type,
            )

            # Step 4: Create entity
            entity = Entity(
                entity_id=entity_id,
                entity_type=input_type,
                content=input_data,
                metadata=metadata,
                status=STATUS_QUEUED,
                validation_errors=validation["errors"],
            )

            # Step 5: Route only if validation succeeds
            if validation["valid"]:

                entity.routing_decision = self.route_input(
                    input_type
                )

                entity.update_status(STATUS_QUEUED)

            else:

                entity.routing_decision = None
                entity.update_status(STATUS_FAILED)

            return entity

        except Exception as exc:

            entity = Entity(
                entity_id=entity_id,
                entity_type="unknown",
                content=input_data,
                status=STATUS_FAILED,
                validation_errors=[str(exc)],
            )

            return entity