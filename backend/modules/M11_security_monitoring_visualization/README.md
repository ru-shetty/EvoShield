MODULE 11 – SECURITY MONITORING AND VISUALIZATION



INTRODUCTION

This module provides centralized security monitoring and visualization for EvoShield. It collects security events from backend modules and displays monitoring information through dashboards and APIs.



PURPOSE

To provide a unified monitoring interface for threat detection results, risk assessment, clustering information, concept drift events, rollback events, scan history, and notifications.



INPUT

\- REST API data

\- Scan history

\- Risk assessment results

\- Cluster information

\- Drift events

\- Rollback events

\- Notifications



OUTPUT

\- Dashboard overview

\- Scan statistics

\- Threat monitoring

\- Risk monitoring

\- Cluster visualization

\- Drift monitoring

\- Rollback monitoring

\- History records

\- Notifications



ALGORITHM USED

Monitoring Dashboard Aggregation Algorithm



Steps:

1\. Receive monitoring data.

2\. Validate required fields.

3\. Process monitoring metrics.

4\. Generate dashboard sections.

5\. Create overview statistics.

6\. Display threat information.

7\. Display risk information.

8\. Display cluster information.

9\. Display drift and rollback information.

10\. Display notifications.



CHANGES FROM EXISTING SYSTEM

Existing systems typically provide isolated monitoring dashboards.



This module:

\- Integrates multiple security modules.

\- Provides centralized monitoring.

\- Supports threat visualization.

\- Supports drift and rollback monitoring.

\- Supports real-time notifications.

\- Supports future mobile integration.



MOBILE AND LAPTOP SUPPORT



Laptop:

\- React Web Dashboard



Mobile:

\- Flutter Android Application



Both platforms consume the same REST API.



IMPLEMENTATION DETAILS



Backend:

\- Python

\- Django

\- Django REST Framework



Frontend:

\- React (Web)

\- Flutter (Android)



MODULE FLOW



REST API

→ Processor

→ Schema Validation

→ Monitoring Dashboard Engine

→ Service Layer

→ Dashboard Response



AUTHOR

EvoShield Security Platform

