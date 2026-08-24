# M04 - Visual Content OCR Analysis

## Overview

M04 is responsible for analyzing text extracted from visual
content through OCR and identifying characteristics that may
indicate suspicious or malicious activity.

The module receives OCR-extracted text and an OCR confidence
value, extracts threat-related features, calculates a weighted
risk score, and produces a standardized analysis result.

---

## Module Responsibilities

- Accept OCR-extracted textual input.
- Accept and validate OCR confidence.
- Detect suspicious keywords.
- Detect suspicious phrases.
- Detect unusually high text density.
- Detect low OCR confidence.
- Detect financial-related content.
- Detect credential-related content.
- Calculate a weighted threat score.
- Assign a risk level.
- Return a standardized analysis result.

---

## Directory Structure

```text
M04_visual_content_ocr_analysis/
│
├── algorithms/
│   ├── __init__.py
│   └── ocr_analyzer.py
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