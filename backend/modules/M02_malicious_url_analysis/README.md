# M02 - Malicious URL Analysis

## Overview

M02 is responsible for analyzing URLs and identifying characteristics
that may indicate malicious, suspicious, or potentially unsafe behavior.

The module receives a URL, extracts security-related features, calculates
a weighted risk score, and produces a standardized analysis result.

---

## Module Responsibilities

- Accept URL input.
- Validate the URL through the API layer.
- Extract suspicious URL characteristics.
- Detect IP-based URLs.
- Detect suspicious URL schemes.
- Detect suspicious keywords.
- Detect unusually long URLs.
- Detect excessive special characters.
- Detect suspicious executable/script extensions.
- Calculate a weighted risk score.
- Assign a risk level.
- Return a standardized analysis result.

---

## Directory Structure

```text
M02_malicious_url_analysis/
│
├── algorithms/
│   ├── __init__.py
│   └── url_analyzer.py
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