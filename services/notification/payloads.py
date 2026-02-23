"""
Payload construction utilities for notification services, providing functions to build message payloads for different notification channels such as Slack, Microsoft Teams, and PagerDuty based on alert data. This module includes functions to extract relevant information from alert objects, format alert details into human-readable text, and construct structured payloads that conform to the expected formats of each notification channel. The utilities ensure that notifications are informative and properly formatted to facilitate quick understanding and response by recipients when alerts are triggered or resolved.

Copyright (c) 2026 Stefan Kumarasinghe

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
"""

from datetime import datetime

from models.alerting.alerts import Alert

NO_VALUE = "(none)"

PD_SEVERITY_MAP = {
    "critical": "critical",
    "high": "critical",
    "error": "error",
    "warning": "warning",
    "info": "info",
}


def _fmt(value) -> str:
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value) if value is not None else "unknown"


def get_label(alert: Alert, key: str, default: str = "") -> str:
    return str((alert.labels or {}).get(key, default))


def get_annotation(alert: Alert, key: str) -> str | None:
    value = (alert.annotations or {}).get(key)
    return str(value) if value is not None else None


def get_alert_text(alert: Alert) -> str:
    summary = get_annotation(alert, "summary")
    description = get_annotation(alert, "description")
    if summary and description and summary != description:
        return f"{summary}\n{description}"
    return summary or description or "No description"


def format_alert_body(alert: Alert, action: str) -> str:
    summary = get_annotation(alert, "summary") or "No summary"
    description = get_annotation(alert, "description") or "No description"

    lines = [
        f"Alert: {get_label(alert, 'alertname', 'Unknown')}",
        f"Status: {action}",
        f"Severity: {get_label(alert, 'severity', 'unknown')}",
        f"Started: {_fmt(alert.starts_at)}",
        "",
        "Summary:",
        summary,
        "",
        "Description:",
        description,
        "",
        "Labels:",
    ]

    for key, value in (alert.labels or {}).items():
        lines.append(f"  {key}: {value}")

    return "\n".join(lines)


def build_slack_payload(alert: Alert, action: str) -> dict:
    severity = get_label(alert, "severity").lower()

    if action == "firing":
        color = "danger"
    elif action == "resolved":
        color = "good"
    else:
        color = "warning"

    ts = (
        int(alert.starts_at.timestamp())
        if isinstance(alert.starts_at, datetime)
        else None
    )

    attachment = {
        "color": color,
        "title": f"[{action.upper()}] {get_label(alert, 'alertname', 'Alert')}",
        "text": get_alert_text(alert),
        "fields": [
            {"title": "Severity", "value": severity or "unknown", "short": True},
            {"title": "Status", "value": action, "short": True},
            {"title": "Summary", "value": get_annotation(alert, "summary") or NO_VALUE, "short": False},
            {"title": "Description", "value": get_annotation(alert, "description") or NO_VALUE, "short": False},
        ],
        "footer": f"Started: {_fmt(alert.starts_at)}",
    }

    if ts is not None:
        attachment["ts"] = ts

    return {"attachments": [attachment]}


def build_teams_payload(alert: Alert, action: str) -> dict:
    severity = get_label(alert, "severity").lower()

    if action == "firing":
        theme_color = "FFA500" if severity == "warning" else "FF0000"
    elif action == "resolved":
        theme_color = "00FF00"
    else:
        theme_color = "FFA500"

    return {
        "@type": "MessageCard",
        "@context": "https://schema.org/extensions",
        "themeColor": theme_color,
        "title": f"[{action.upper()}] {get_label(alert, 'alertname', 'Alert')}",
        "text": get_alert_text(alert),
        "sections": [{
            "facts": [
                {"name": "Severity", "value": severity or "unknown"},
                {"name": "Status", "value": action},
                {"name": "Started", "value": _fmt(alert.starts_at)},
                {"name": "Summary", "value": get_annotation(alert, "summary") or NO_VALUE},
                {"name": "Description", "value": get_annotation(alert, "description") or NO_VALUE},
            ]
        }]
    }


def build_pagerduty_payload(alert: Alert, action: str, routing_key: str) -> dict:
    event_action = "trigger" if action == "firing" else "resolve"

    raw_severity = get_label(alert, "severity", "warning").lower()
    severity = PD_SEVERITY_MAP.get(raw_severity, "warning")

    summary = get_annotation(alert, "summary")
    description = get_annotation(alert, "description")

    return {
        "routing_key": routing_key,
        "event_action": event_action,
        "dedup_key": alert.fingerprint or get_label(alert, "alertname", "alert"),
        "payload": {
            "summary": summary or description or get_label(alert, "alertname", "Alert"),
            "severity": severity,
            "source": get_label(alert, "instance", "unknown"),
            "custom_details": {
                "labels": alert.labels or {},
                "annotations": alert.annotations or {},
            },
        },
    }
