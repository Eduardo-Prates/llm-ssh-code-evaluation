from __future__ import annotations

import re
from collections import defaultdict, deque
from datetime import datetime, timedelta


_FAILED_RE = re.compile(
    r"^(?P<timestamp>\S+)\s+sshd:\s+Failed password for "
    r"(?:(?:invalid user)\s+)?(?P<user>\S+)\s+from\s+"
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

    ip = match.group("ip")
    user = match.group("user")

    if not ip or not user:
        return None

    return {
        "timestamp": timestamp,
        "ip": ip,
        "user": user,
    }


def detect_brute_force(
    lines: list[str],
    threshold: int = 5,
    window_seconds: int = 60,
) -> list[dict]:
    if threshold <= 0 or window_seconds < 0:
        return []

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

        current = windows[ip]
        cutoff = event["timestamp"] - window

        while current and current[0]["timestamp"] < cutoff:
            current.popleft()

        current.append(event)

        if len(current) >= threshold:
            selected = list(current)[-threshold:]
            alerts.append(
                {
                    "ip": ip,
                    "failures": threshold,
                    "users": sorted({item["user"] for item in selected}),
                    "start": selected[0]["timestamp"].strftime("%Y-%m-%dT%H:%M:%S"),
                    "end": selected[-1]["timestamp"].strftime("%Y-%m-%dT%H:%M:%S"),
                }
            )
            alerted_ips.add(ip)

    alerts.sort(key=lambda alert: (alert["start"], alert["ip"]))
    return alerts
