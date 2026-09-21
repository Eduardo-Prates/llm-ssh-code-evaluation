from __future__ import annotations

from collections import defaultdict, deque
from datetime import datetime, timedelta
import re


_FAILED_RE = re.compile(
    r"^(?P<timestamp>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})\s+"
    r"sshd:\s+Failed password for\s+"
    r"(?:(?:invalid user)\s+)?(?P<user>\S+)\s+"
    r"from\s+(?P<ip>\S+)\s+port\s+\d+\s+ssh2\s*$"
)


def parse_log_line(line: str) -> dict | None:
    if not line or not line.strip():
        return None

    match = _FAILED_RE.match(line.strip())
    if not match:
        return None

    try:
        timestamp = datetime.fromisoformat(match.group("timestamp"))
    except ValueError:
        return None

    if timestamp.tzinfo is not None:
        timestamp = timestamp.replace(tzinfo=None)

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
        parsed = parse_log_line(line)
        if parsed is not None:
            events.append(parsed)

    events.sort(key=lambda event: (event["timestamp"], event["ip"], event["user"]))

    per_ip: dict[str, deque[dict]] = defaultdict(deque)
    alerted_ips: set[str] = set()
    alerts: list[dict] = []
    window = timedelta(seconds=window_seconds)

    for event in events:
        ip = event["ip"]

        if ip in alerted_ips:
            continue

        queue = per_ip[ip]
        queue.append(event)

        while queue and event["timestamp"] - queue[0]["timestamp"] > window:
            queue.popleft()

        if len(queue) >= threshold:
            first_threshold_events = list(queue)[:threshold]
            users = sorted({item["user"] for item in first_threshold_events})

            alerts.append(
                {
                    "ip": ip,
                    "failures": threshold,
                    "users": users,
                    "start": first_threshold_events[0]["timestamp"].strftime(
                        "%Y-%m-%dT%H:%M:%S"
                    ),
                    "end": first_threshold_events[-1]["timestamp"].strftime(
                        "%Y-%m-%dT%H:%M:%S"
                    ),
                }
            )
            alerted_ips.add(ip)

    alerts.sort(key=lambda alert: (alert["start"], alert["ip"]))
    return alerts
