"""Analisador simplificado de logs SSH para detecção de força bruta."""

from __future__ import annotations

import ipaddress
import re
from collections import deque
from datetime import datetime, timedelta

_TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S"

_FAILED_RE = re.compile(
    r"^(?P<ts>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})\s+"
    r"sshd(?:\[\d+\])?:\s+"
    r"Failed password for (?:invalid user )?(?P<user>\S+) "
    r"from (?P<ip>\S+) port (?P<port>\d+)(?:\s+ssh2)?\s*$"
)


def parse_log_line(line: str) -> dict | None:
    """Converte uma linha de log em evento de falha ou retorna None."""
    if not isinstance(line, str):
        return None

    text = line.strip()
    if not text:
        return None

    match = _FAILED_RE.match(text)
    if match is None:
        return None

    try:
        timestamp = datetime.strptime(match.group("ts"), _TIMESTAMP_FORMAT)
    except ValueError:
        return None

    ip = match.group("ip")
    try:
        ipaddress.ip_address(ip)
    except ValueError:
        return None

    return {"timestamp": timestamp, "ip": ip, "user": match.group("user")}


def detect_brute_force(
    lines: list[str], threshold: int = 5, window_seconds: int = 60
) -> list[dict]:
    """Detecta o primeiro alerta de força bruta por IP em janela móvel."""
    if threshold < 1:
        raise ValueError("threshold deve ser maior ou igual a 1")
    if window_seconds < 0:
        raise ValueError("window_seconds não pode ser negativo")

    events = []
    for line in lines:
        event = parse_log_line(line)
        if event is not None:
            events.append(event)

    # sort estável: preserva a ordem original em caso de timestamps iguais
    events.sort(key=lambda e: e["timestamp"])

    window = timedelta(seconds=window_seconds)
    windows: dict[str, deque] = {}
    alerted: set[str] = set()
    alerts: list[dict] = []

    for event in events:
        ip = event["ip"]
        if ip in alerted:
            continue

        current = windows.setdefault(ip, deque())
        current.append(event)

        while current and event["timestamp"] - current[0]["timestamp"] > window:
            current.popleft()

        if len(current) >= threshold:
            alerts.append(
                {
                    "ip": ip,
                    "failures": threshold,
                    "users": sorted({e["user"] for e in current}),
                    "start": current[0]["timestamp"].strftime(_TIMESTAMP_FORMAT),
                    "end": event["timestamp"].strftime(_TIMESTAMP_FORMAT),
                }
            )
            alerted.add(ip)
            del windows[ip]

    alerts.sort(key=lambda a: (a["start"], a["ip"]))
    return alerts
