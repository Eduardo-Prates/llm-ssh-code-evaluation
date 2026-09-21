import re
from datetime import datetime, timedelta

def parse_log_line(line: str) -> dict | None:
    date_match = re.match(r'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})', line)
    if not date_match:
        return None
    
    dt_str = date_match.group(1)
    
    if "Failed password for" not in line:
        return None
        
    match = re.search(r'Failed password for (?:invalid user )?(\S+) from (\S+)', line)
    if match:
        user, ip = match.groups()
        try:
            dt = datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%S")
            return {"timestamp": dt, "ip": ip, "user": user}
        except ValueError:
            return None
    return None

def detect_brute_force(lines: list[str], threshold: int = 5, window_seconds: int = 60) -> list[dict]:
    events = []
    for line in lines:
        parsed = parse_log_line(line)
        if parsed:
            events.append(parsed)
            
    events.sort(key=lambda x: x["timestamp"])
    
    alerts = []
    alerted_ips = set()
    ip_events = {}
    
    for event in events:
        ip = event["ip"]
        if ip in alerted_ips:
            continue
            
        if ip not in ip_events:
            ip_events[ip] = []
            
        ip_events[ip].append(event)
        
        current_time = event["timestamp"]
        window_start_limit = current_time - timedelta(seconds=window_seconds)
        
        valid_events = [e for e in ip_events[ip] if e["timestamp"] >= window_start_limit]
        ip_events[ip] = valid_events
        
        if len(valid_events) >= threshold:
            alert_events = valid_events[-threshold:]
            start_time = alert_events[0]["timestamp"]
            end_time = alert_events[-1]["timestamp"]
            users = sorted(list(set(e["user"] for e in alert_events)))
            
            alerts.append({
                "ip": ip,
                "failures": threshold,
                "users": users,
                "start": start_time.strftime("%Y-%m-%dT%H:%M:%S"),
                "end": end_time.strftime("%Y-%m-%dT%H:%M:%S")
            })
            alerted_ips.add(ip)
            
    alerts.sort(key=lambda x: (x["start"], x["ip"]))
    return alerts
