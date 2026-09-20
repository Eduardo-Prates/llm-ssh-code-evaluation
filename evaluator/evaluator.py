from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
import time


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT))

from tests.test_cases import TESTS


PROTOCOL_VERSION = "1.0"
WORKER_PATH = Path(__file__).with_name("worker.py")


def missing_delivery_result(test: dict) -> dict:
    return {
        "id": test["id"],
        "name": test["name"],
        "group": test["group"],
        "status": "failed",
        "duration_ms": 0,
        "error_type": "DeliveryError",
        "message": "solution.py não foi fornecido como arquivo baixável",
    }


def run_one_test(solution_path: Path, test: dict, timeout_seconds: float) -> dict:
    command = [
        sys.executable,
        str(WORKER_PATH),
        "--solution",
        str(solution_path),
        "--test-id",
        test["id"],
    ]
    started = time.perf_counter()
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return {
            "id": test["id"],
            "name": test["name"],
            "group": test["group"],
            "status": "failed",
            "duration_ms": round((time.perf_counter() - started) * 1000, 3),
            "error_type": "TimeoutExpired",
            "message": f"tempo máximo de {timeout_seconds:g} segundos excedido",
        }

    output_lines = [line for line in completed.stdout.splitlines() if line.strip()]
    if output_lines:
        try:
            return json.loads(output_lines[-1])
        except json.JSONDecodeError:
            pass
    return {
        "id": test["id"],
        "name": test["name"],
        "group": test["group"],
        "status": "failed",
        "duration_ms": round((time.perf_counter() - started) * 1000, 3),
        "error_type": "WorkerError",
        "message": "o processo de teste não produziu um resultado JSON válido",
        "worker_exit_code": completed.returncode,
        "worker_stdout": completed.stdout[-2000:],
        "worker_stderr": completed.stderr[-2000:],
    }


def evaluate(solution_path: Path, timeout_seconds: float) -> dict:
    solution_path = solution_path.resolve()
    delivery_error = not solution_path.is_file() or solution_path.name != "solution.py"
    if delivery_error:
        test_results = [missing_delivery_result(test) for test in TESTS]
    else:
        test_results = [run_one_test(solution_path, test, timeout_seconds) for test in TESTS]

    passed = sum(result["status"] == "passed" for result in test_results)
    total = len(TESTS)
    return {
        "protocol_version": PROTOCOL_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "python_version": platform_version(),
        "solution": str(solution_path),
        "timeout_seconds_per_test": timeout_seconds,
        "delivery_error": delivery_error,
        "total": total,
        "passed": passed,
        "failed": total - passed,
        "score": round(passed / total * 100, 2),
        "tests": test_results,
    }


def platform_version() -> str:
    return ".".join(str(part) for part in sys.version_info[:3])


def write_report(report: dict, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Executa a bateria padronizada contra solution.py")
    parser.add_argument("--solution", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--timeout", type=float, default=3.0, help="limite em segundos por teste")
    args = parser.parse_args()
    if args.timeout <= 0:
        parser.error("--timeout deve ser maior que zero")
    report = evaluate(args.solution, args.timeout)
    write_report(report, args.output)
    print(
        f"Resultado: {report['passed']}/{report['total']} testes; "
        f"pontuação {report['score']:.2f}; delivery_error={str(report['delivery_error']).lower()}"
    )
    return 0 if report["failed"] == 0 else (2 if report["delivery_error"] else 1)


if __name__ == "__main__":
    raise SystemExit(main())

