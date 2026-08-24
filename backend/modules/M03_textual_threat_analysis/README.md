# M03 - Textual Threat Analysis

## Overview

M03 is responsible for analyzing textual content and identifying
characteristics that may indicate suspicious, malicious, or
social-engineering-related activity.

The module receives text, extracts threat-related features,
calculates a weighted risk score, and produces a standardized
analysis result.

---

## Module Responsibilities

- Accept textual input.
- Validate text through the API layer.
- Detect suspicious keywords.
- Detect known threat phrases.
- Detect urgency-related language.
- Detect credential requests.
- Detect financial requests.
- Detect excessive special characters.
- Calculate a weighted threat score.
- Assign a risk level.
- Return a standardized analysis result.

---

## Directory Structure

```text
M03_textual_threat_analysis/
│
├── algorithms/
│   ├── __init__.py
│   └── text_analyzer.py
│
├── api/
│   ├── __init__.py
│   ├── serializers.py
│   ├── urls.py
│   └── views.py
│
├── models/
│   ├── __init__.py
│   └── models.py
│
├── processors/
│   ├── __init__.py
│   └── processor.py
│
├── schemas/
│   └── schemas.py
│
├── services/
│   ├── __init__.py
│   └── service.py
│
├── tests/
│   ├── __init__.py
│   ├── test_algorithm.py
│   ├── test_service.py
│   └── test_api.py
│
├── config.py
└── README.md