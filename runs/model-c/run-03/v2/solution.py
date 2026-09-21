"""Analisador simplificado de logs SSH para detecção de força bruta."""

from __future__ import annotations

import ipaddress
import re
from collections import deque
from datetime import datetime

_TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S"

_FAILED_PATTERN = re.compile(
    r"(?P<timestamp>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})"
    r"\s+sshd(?:\[\d+\])?:\s+"
    r"Failed password for\s+(?:invalid user\s+)?(?P<user>\S+)"
    r"\s+from\s+(?P<ip>\S+)"
    r"\s+port\s+\d+"
    r"(?:\s+ssh\d*)?"
)


def parse_log_line(line: str) -> dict | None:
    """Analisa uma linha de log e retorna os dados de uma falha de autenticação.

    Retorna None para linhas aceitas, desconhecidas, vazias ou malformadas.
    """
    if not isinstance(line, str):
        return None

    text = line.strip()
    if not text:
        return None

    match = _FAILED_PATTERN.fullmatch(text)
    if match is None:
        return None

    try:
        timestamp = datetime.strptime(match.group("timestamp"), _TIMESTAMP_FORMAT)
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
    """Detecta IPs que atingem `threshold` falhas em uma janela móvel.

    A janela é inclusiva: eventos separados por exatamente `window_seconds`
    pertencem à mesma janela. Somente o primeiro alerta de cada IP é gerado.
    """
    if threshold < 1:
        raise ValueError("threshold deve ser maior ou igual a 1")
    if window_seconds < 0:
        raise ValueError("window_seconds não pode ser negativo")

    events = []
    for line in lines:
        event = parse_log_line(line)
        if event is not None:
            events.append(event)

    # sort() é estável: eventos com o mesmo timestamp mantêm a ordem de entrada.
    events.sort(key=lambda e: e["timestamp"])

    windows: dict[str, deque] = {}
    alerted: set[str] = set()
    alerts: list[dict] = []

    for event in events:
        ip = event["ip"]
        if ip in alerted:
            continue

        timestamp = event["timestamp"]
        window = windows.setdefault(ip, deque())
        window.append((timestamp, event["user"]))

        while (timestamp - window[0][0]).total_seconds() > window_seconds:
            window.popleft()

        if len(window) >= threshold:
            alerts.append(
                {
                    "ip": ip,
                    "failures": threshold,
                    "users": sorted({user for _, user in window}),
                    "start": window[0][0].strftime(_TIMESTAMP_FORMAT),
                    "end": timestamp.strftime(_TIMESTAMP_FORMAT),
                }
            )
            alerted.add(ip)
            del windows[ip]

    alerts.sort(key=lambda a: (a["start"], a["ip"]))
    return alerts
