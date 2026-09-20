from __future__ import annotations

from datetime import datetime


class TestFailure(AssertionError):
    def __init__(self, expected: object, actual: object):
        super().__init__(f"expected {expected!r}, got {actual!r}")
        self.expected = repr(expected)
        self.actual = repr(actual)


def assert_equal(actual: object, expected: object) -> None:
    if actual != expected:
        raise TestFailure(expected, actual)


def failed(at: str, user: str = "root", ip: str = "192.0.2.10", port: int = 50001) -> str:
    return f"{at} sshd: Failed password for {user} from {ip} port {port} ssh2"


def invalid_user(at: str, user: str = "admin", ip: str = "192.0.2.10", port: int = 50001) -> str:
    return f"{at} sshd: Failed password for invalid user {user} from {ip} port {port} ssh2"


def expected_alert(ip: str, failures: int, users: list[str], start: str, end: str) -> dict:
    return {"ip": ip, "failures": failures, "users": users, "start": start, "end": end}


def t01(module) -> None:
    actual = module.parse_log_line(failed("2026-09-20T10:00:00", user="eduardo"))
    expected = {"timestamp": datetime(2026, 9, 20, 10, 0, 0), "ip": "192.0.2.10", "user": "eduardo"}
    assert_equal(actual, expected)


def t02(module) -> None:
    actual = module.parse_log_line(invalid_user("2026-09-20T10:00:00", user="admin"))
    expected = {"timestamp": datetime(2026, 9, 20, 10, 0, 0), "ip": "192.0.2.10", "user": "admin"}
    assert_equal(actual, expected)


def t03(module) -> None:
    line = "2026-09-20T10:00:00 sshd: Accepted password for eduardo from 192.0.2.10 port 50001 ssh2"
    assert_equal(module.parse_log_line(line), None)


def t04(module) -> None:
    assert_equal(module.parse_log_line("2026-99-99T25:61:61 sshd: Failed password"), None)


def t05(module) -> None:
    assert_equal(module.parse_log_line("2026-09-20T10:00:00 kernel: interface changed state"), None)


def t06(module) -> None:
    line = failed("2026-09-20T10:00:00", ip="2001:db8::10")
    actual = module.parse_log_line(line)
    assert_equal(actual["ip"] if actual else None, "2001:db8::10")


def t07(module) -> None:
    times = ["00", "10", "20", "30", "59"]
    lines = [failed(f"2026-09-20T10:00:{second}", user=f"u{i}") for i, second in enumerate(times)]
    expected = [expected_alert("192.0.2.10", 5, ["u0", "u1", "u2", "u3", "u4"], "2026-09-20T10:00:00", "2026-09-20T10:00:59")]
    assert_equal(module.detect_brute_force(lines), expected)


def t08(module) -> None:
    lines = [failed(f"2026-09-20T10:0{i}:00") for i in range(5)]
    assert_equal(module.detect_brute_force(lines), [])


def t09(module) -> None:
    seconds = [0, 15, 30, 45]
    lines = [failed(f"2026-09-20T10:00:{second:02d}") for second in seconds]
    lines.append(failed("2026-09-20T10:01:00"))
    actual = module.detect_brute_force(lines)
    assert_equal(len(actual), 1)
    assert_equal(actual[0]["start"], "2026-09-20T10:00:00")
    assert_equal(actual[0]["end"], "2026-09-20T10:01:00")


def t10(module) -> None:
    lines = [failed(f"2026-09-20T10:00:{second:02d}") for second in [40, 10, 30, 0, 20]]
    actual = module.detect_brute_force(lines)
    assert_equal(len(actual), 1)
    assert_equal((actual[0]["start"], actual[0]["end"]), ("2026-09-20T10:00:00", "2026-09-20T10:00:40"))


def t11(module) -> None:
    lines = []
    for ip in ["192.0.2.20", "192.0.2.10"]:
        for second in [0, 10, 20]:
            lines.append(failed(f"2026-09-20T10:00:{second:02d}", ip=ip))
    actual = module.detect_brute_force(lines, threshold=3)
    assert_equal([item["ip"] for item in actual], ["192.0.2.10", "192.0.2.20"])


def t12(module) -> None:
    lines = [failed(f"2026-09-20T10:00:{second:02d}") for second in [0, 10, 20, 30, 40, 50]]
    actual = module.detect_brute_force(lines)
    assert_equal(len(actual), 1)
    assert_equal(actual[0]["end"], "2026-09-20T10:00:40")


def t13(module) -> None:
    users = ["root", "admin", "root", "alice", "admin"]
    lines = [failed(f"2026-09-20T10:00:{i * 10:02d}", user=user) for i, user in enumerate(users)]
    actual = module.detect_brute_force(lines)
    assert_equal(actual[0]["users"], ["admin", "alice", "root"])


def t14(module) -> None:
    lines = [failed(f"2026-09-20T10:00:{second:02d}") for second in [0, 10, 20]]
    actual = module.detect_brute_force(lines, threshold=3)
    assert_equal(actual[0]["failures"], 3)


def t15(module) -> None:
    lines = [failed(f"2026-09-20T10:00:{second:02d}") for second in [0, 7, 14, 21, 30]]
    assert_equal(len(module.detect_brute_force(lines, window_seconds=30)), 1)
    assert_equal(module.detect_brute_force(lines, window_seconds=29), [])


def t16(module) -> None:
    line = failed("2026-09-20T10:00:00", user="admin")
    actual = module.detect_brute_force([line], threshold=1)
    expected = [expected_alert("192.0.2.10", 1, ["admin"], "2026-09-20T10:00:00", "2026-09-20T10:00:00")]
    assert_equal(actual, expected)


def t17(module) -> None:
    lines = [
        failed("2026-09-20T10:00:01", ip="192.0.2.20"),
        failed("2026-09-20T10:00:00", ip="192.0.2.20"),
        failed("2026-09-20T10:00:01", ip="192.0.2.10"),
        failed("2026-09-20T10:00:00", ip="192.0.2.10"),
    ]
    actual = module.detect_brute_force(lines, threshold=2)
    assert_equal([item["ip"] for item in actual], ["192.0.2.10", "192.0.2.20"])


def t18(module) -> None:
    lines = [failed(f"2026-09-20T10:00:{second:02d}", user="root") for second in [0, 10, 20, 30, 40]]
    actual = module.detect_brute_force(lines)
    assert_equal(len(actual), 1)
    alert = actual[0]
    assert_equal(set(alert), {"ip", "failures", "users", "start", "end"})
    assert_equal((type(alert["ip"]), type(alert["failures"]), type(alert["users"]), type(alert["start"]), type(alert["end"])), (str, int, list, str, str))
    datetime.strptime(alert["start"], "%Y-%m-%dT%H:%M:%S")
    datetime.strptime(alert["end"], "%Y-%m-%dT%H:%M:%S")


def t19(module) -> None:
    assert_equal(module.detect_brute_force([]), [])


def t20(module) -> None:
    lines = [
        "",
        "texto desconhecido",
        failed("2026-09-20T10:00:00", user="root"),
        "2026-09-20T10:00:05 sshd: Accepted password for eduardo from 192.0.2.10 port 50001 ssh2",
        invalid_user("2026-09-20T10:00:10", user="admin"),
        "2026-99-99T10:00:15 sshd: Failed password for root from 192.0.2.10 port 50001 ssh2",
        failed("2026-09-20T10:00:20", user="guest"),
    ]
    actual = module.detect_brute_force(lines, threshold=3)
    assert_equal(len(actual), 1)
    assert_equal(actual[0]["users"], ["admin", "guest", "root"])


TESTS = [
    {"id": "T01", "name": "parse_valid_user", "group": "parser", "call": t01},
    {"id": "T02", "name": "parse_invalid_user", "group": "parser", "call": t02},
    {"id": "T03", "name": "accepted_returns_none", "group": "parser", "call": t03},
    {"id": "T04", "name": "malformed_returns_none", "group": "parser", "call": t04},
    {"id": "T05", "name": "unrelated_returns_none", "group": "parser", "call": t05},
    {"id": "T06", "name": "ipv6_address", "group": "parser", "call": t06},
    {"id": "T07", "name": "five_failures_under_60_seconds", "group": "detection", "call": t07},
    {"id": "T08", "name": "five_failures_over_60_seconds", "group": "detection", "call": t08},
    {"id": "T09", "name": "exact_60_second_boundary", "group": "detection", "call": t09},
    {"id": "T10", "name": "out_of_order_events", "group": "detection", "call": t10},
    {"id": "T11", "name": "two_distinct_ips", "group": "detection", "call": t11},
    {"id": "T12", "name": "only_first_alert_per_ip", "group": "detection", "call": t12},
    {"id": "T13", "name": "unique_sorted_users", "group": "detection", "call": t13},
    {"id": "T14", "name": "custom_threshold", "group": "detection", "call": t14},
    {"id": "T15", "name": "custom_window", "group": "detection", "call": t15},
    {"id": "T16", "name": "threshold_one", "group": "detection", "call": t16},
    {"id": "T17", "name": "alerts_sorted_by_start_and_ip", "group": "output", "call": t17},
    {"id": "T18", "name": "exact_fields_types_and_iso_format", "group": "output", "call": t18},
    {"id": "T19", "name": "empty_input", "group": "robustness", "call": t19},
    {"id": "T20", "name": "mixed_valid_invalid_and_unrelated", "group": "robustness", "call": t20},
]


def find_test(test_id: str) -> dict:
    for test in TESTS:
        if test["id"] == test_id:
            return test
    raise KeyError(test_id)

