from __future__ import annotations

import re
from collections import defaultdict, deque
from datetime import datetime, timedelta


_FAILED_RE = re.compile(
    r"^(?P<timestamp>\S+)\s+sshd:\s+Failed password for "
    r"(?:(?:invalid user)\s+)?(?P<user>\S+)\s+from "
    r"(?P<ip>\S+)\s+port\s+\d+\s+ssh2\s*$"
)


def parse_log_line(line: str) -> dict | None:
    if not isinstance(line, str) or not line.strip():
        return None

    match = _FAILED_RE.match(line.strip())
    if match is None:
        return None

    try:
        timestamp = datetime.fromisoformat(match.group("timestamp"))
    except ValueError:
        return None

    if timestamp.tzinfo is not None:
        return None

    return {
        "timestamp": timestamp,
        "ip": match.group("ip"),
        "user": match.group("user"),
    }


def detect_brute_force(
    lines: list[str],
    threshold: int = 5,
    window_seconds: int = 60,
) -> list[dict]:
    if threshold <= 0:
        raise ValueError("threshold must be greater than zero")
    if window_seconds < 0:
        raise ValueError("window_seconds must be non-negative")

    events = []
    for line in lines:
        event = parse_log_line(line)
        if event is not None:
            events.append(event)

    events.sort(key=lambda event: event["timestamp"])

    windows: dict[str, deque[dict]] = defaultdict(deque)
    alerted_ips: set[str] = set()
    alerts: list[dict] = []
    window = timedelta(seconds=window_seconds)

    for event in events:
        ip = event["ip"]
        if ip in alerted_ips:
            continue

        current_window = windows[ip]
        cutoff = event["timestamp"] - window

        while current_window and current_window[0]["timestamp"] < cutoff:
            current_window.popleft()

        current_window.append(event)

        if len(current_window) >= threshold:
            first_threshold_events = list(current_window)[-threshold:]
            start = first_threshold_events[0]["timestamp"]
            end = event["timestamp"]
            users = sorted({item["user"] for item in current_window})

            alerts.append(
                {
                    "ip": ip,
                    "failures": threshold,
                    "users": users,
                    "start": start.strftime("%Y-%m-%dT%H:%M:%S"),
                    "end": end.strftime("%Y-%m-%dT%H:%M:%S"),
                }
            )
            alerted_ips.add(ip)

    alerts.sort(key=lambda alert: (alert["start"], alert["ip"]))
    return alerts
