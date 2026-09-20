from __future__ import annotations

import argparse
from contextlib import redirect_stderr, redirect_stdout
import importlib.util
import io
import json
from pathlib import Path
import sys
import time
import traceback


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT))

from tests.test_cases import TestFailure, find_test


def load_solution(path: Path):
    spec = importlib.util.spec_from_file_location("evaluated_solution", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"não foi possível carregar {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_test(solution_path: Path, test_id: str) -> dict:
    test = find_test(test_id)
    captured_stdout = io.StringIO()
    captured_stderr = io.StringIO()
    started = time.perf_counter()
    try:
        with redirect_stdout(captured_stdout), redirect_stderr(captured_stderr):
            module = load_solution(solution_path)
            test["call"](module)
        status = "passed"
        details = {}
    except TestFailure as error:
        status = "failed"
        details = {
            "error_type": type(error).__name__,
            "expected": error.expected,
            "actual": error.actual,
        }
    except BaseException as error:
        status = "failed"
        details = {
            "error_type": type(error).__name__,
            "message": str(error),
            "traceback": "".join(traceback.format_exception_only(type(error), error)).strip(),
        }
    duration_ms = round((time.perf_counter() - started) * 1000, 3)
    result = {
        "id": test["id"],
        "name": test["name"],
        "group": test["group"],
        "status": status,
        "duration_ms": duration_ms,
    }
    result.update(details)
    if captured_stdout.getvalue():
        result["captured_stdout"] = captured_stdout.getvalue()[-2000:]
    if captured_stderr.getvalue():
        result["captured_stderr"] = captured_stderr.getvalue()[-2000:]
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--solution", required=True, type=Path)
    parser.add_argument("--test-id", required=True)
    args = parser.parse_args()
    result = run_test(args.solution.resolve(), args.test_id)
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

