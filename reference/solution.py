from __future__ import annotations

from collections import defaultdict, deque
from datetime import datetime
import ipaddress
import re


_FAILED_PATTERN = re.compile(
    r"^(?P<timestamp>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})\s+"
    r"sshd:\s+Failed password for "
    r"(?:(?:invalid user )?)(?P<user>\S+)\s+"
    r"from\s+(?P<ip>\S+)\s+port\s+\d+\s+ssh2\s*$"
)


def parse_log_line(line: str) -> dict | None:
    if not isinstance(line, str):
        return None
    match = _FAILED_PATTERN.fullmatch(line.strip())
    if match is None:
        return None
    try:
        timestamp = datetime.fromisoformat(match.group("timestamp"))
        ipaddress.ip_address(match.group("ip"))
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
    lines: list[str], threshold: int = 5, window_seconds: int = 60
) -> list[dict]:
    if threshold < 1:
        raise ValueError("threshold must be at least 1")
    if window_seconds < 0:
        raise ValueError("window_seconds must not be negative")

    events = [event for line in lines if (event := parse_log_line(line)) is not None]
    events.sort(key=lambda event: (event["timestamp"], event["ip"], event["user"]))

    windows: dict[str, deque[dict]] = defaultdict(deque)
    alerted: set[str] = set()
    alerts: list[dict] = []

    for event in events:
        ip = event["ip"]
        if ip in alerted:
            continue
        window = windows[ip]
        while window and (event["timestamp"] - window[0]["timestamp"]).total_seconds() > window_seconds:
            window.popleft()
        window.append(event)
        if len(window) == threshold:
            alerts.append(
                {
                    "ip": ip,
                    "failures": threshold,
                    "users": sorted({item["user"] for item in window}),
                    "start": window[0]["timestamp"].strftime("%Y-%m-%dT%H:%M:%S"),
                    "end": window[-1]["timestamp"].strftime("%Y-%m-%dT%H:%M:%S"),
                }
            )
            alerted.add(ip)

    alerts.sort(key=lambda alert: (alert["start"], alert["ip"]))
    return alerts

