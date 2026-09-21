import re
from collections import defaultdict, deque
from datetime import datetime

_FAIL_RE = re.compile(
    r"^\s*(?P<ts>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})\s+sshd(?:\[\d+\])?:\s+"
    r"Failed password for (?:invalid user )?(?P<user>\S+) "
    r"from (?P<ip>\S+) port \d+(?:\s+ssh2)?\s*$"
)

_TS_FMT = "%Y-%m-%dT%H:%M:%S"


def _valid_ip(ip: str) -> bool:
    import ipaddress

    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False


def parse_log_line(line: str) -> dict | None:
    if not isinstance(line, str) or not line.strip():
        return None
    m = _FAIL_RE.match(line)
    if not m:
        return None
    try:
        ts = datetime.strptime(m.group("ts"), _TS_FMT)
    except ValueError:
        return None
    ip = m.group("ip")
    if not _valid_ip(ip):
        return None
    return {"timestamp": ts, "ip": ip, "user": m.group("user")}


def detect_brute_force(
    lines: list[str], threshold: int = 5, window_seconds: int = 60
) -> list[dict]:
    events = []
    for idx, line in enumerate(lines):
        ev = parse_log_line(line)
        if ev is not None:
            events.append((ev["timestamp"], idx, ev["ip"], ev["user"]))
    events.sort(key=lambda e: (e[0], e[1]))

    if threshold < 1:
        threshold = 1

    windows = defaultdict(deque)
    done = set()
    alerts = []

    for ts, _, ip, user in events:
        if ip in done:
            continue
        dq = windows[ip]
        dq.append((ts, user))
        while (ts - dq[0][0]).total_seconds() > window_seconds:
            dq.popleft()
        if len(dq) >= threshold:
            items = list(dq)[-threshold:]
            alerts.append(
                {
                    "ip": ip,
                    "failures": threshold,
                    "users": sorted({u for _, u in items}),
                    "start": items[0][0].strftime(_TS_FMT),
                    "end": items[-1][0].strftime(_TS_FMT),
                }
            )
            done.add(ip)
            del windows[ip]

    alerts.sort(key=lambda a: (a["start"], a["ip"]))
    return alerts
