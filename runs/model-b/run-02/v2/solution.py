import re
from datetime import datetime

def parse_log_line(line: str) -> dict | None:
    match = re.search(
        r'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}).*?sshd(?:\[\d+\])?:\s+Failed password for (?:invalid user )?(\S+) from (\S+)',
        line
    )
    if not match:
        return None
    
    dt_str, user, ip = match.groups()
    try:
        dt = datetime.fromisoformat(dt_str)
        return {"timestamp": dt, "ip": ip, "user": user}
    except ValueError:
        return None

def detect_brute_force(lines: list[str], threshold: int = 5, window_seconds: int = 60) -> list[dict]:
    parsed_events = []
    for line in lines:
        parsed = parse_log_line(line)
        if parsed is not None:
            parsed_events.append(parsed)
            
    parsed_events.sort(key=lambda x: x["timestamp"])
    
    ip_to_events = {}
    for event in parsed_events:
        ip = event["ip"]
        if ip not in ip_to_events:
            ip_to_events[ip] = []
        ip_to_events[ip].append(event)
        
    alerts = []
    
    for ip, events in ip_to_events.items():
        if threshold <= 0:
            continue
            
        for i in range(len(events) - threshold + 1):
            window = events[i : i + threshold]
            start_event = window[0]
            end_event = window[-1]
            
            delta = end_event["timestamp"] - start_event["timestamp"]
            if delta.total_seconds() <= window_seconds:
                users = sorted(list(set(e["user"] for e in window)))
                alerts.append({
                    "ip": ip,
                    "failures": threshold,
                    "users": users,
                    "start": start_event["timestamp"].strftime("%Y-%m-%dT%H:%M:%S"),
                    "end": end_event["timestamp"].strftime("%Y-%m-%dT%H:%M:%S")
                })
                break 
                
    alerts.sort(key=lambda x: (x["start"], x["ip"]))
    
    return alerts
