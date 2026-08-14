# EvoShield - Module 1
## Input Acquisition and Validation Module

### Purpose

The Input Acquisition and Validation Module is the entry point of EvoShield.

It receives supported input modalities, identifies their type, validates them,
creates a unique EntityID, attaches metadata and timestamp information, and
routes the input to the appropriate domain-specific analyzer.

---

## Supported Inputs

- URL
- Text
- Image
- Audio
- Video
- File

---

## Processing Flow

Input
↓
Identify Input Type
↓
Validate Input
↓
Create EntityID
↓
Attach Metadata
↓
Determine Routing Decision
↓
Set Processing Status
↓
Send to Domain Analyzer

---

## Routing

| Input Type | Destination |
|------------|-------------|
| URL | Malicious URL Analysis |
| Text | Textual Threat Analysis |
| Image | Visual Content and OCR Analysis |
| Audio | Speech and Media Intelligence |
| Video | Speech and Media Intelligence |
| File | Malware and Behavioral Analysis |

---

## Example

Input:

https://example.com/login

Output:

{
    "entity_id": "ENT-...",
    "entity_type": "url",
    "status": "QUEUED",
    "routing_decision": "malicious_url_analysis"
}

---

## Module 2 Connection

When Module 1 identifies an input as a URL, it routes the entity to:

malicious_url_analysis

Module 2 then performs malicious URL analysis and returns URL features,
phishing probability and classification.

---

## Status Values

- QUEUED
- PROCESSING
- COMPLETED
- FAILED

---

## Testing

Run:

python -m unittest discover

or:

python -m unittest tests.test_algorithm
python -m unittest tests.test_service
python -m unittest tests.test_api