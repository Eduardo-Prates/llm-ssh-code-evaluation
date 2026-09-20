from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
EVALUATOR = Path(__file__).with_name("evaluator.py")
FEEDBACK = Path(__file__).with_name("generate_feedback.py")
SUMMARY = Path(__file__).with_name("generate_summary.py")


def run(command: list[str]) -> int:
    completed = subprocess.run(command, cwd=REPOSITORY_ROOT, check=False)
    return completed.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description="Avalia todas as combinações previstas no protocolo")
    parser.add_argument("--timeout", type=float, default=3.0)
    args = parser.parse_args()
    for model in ("model-a", "model-b", "model-c"):
        for run_number in range(1, 4):
            for version in ("v1", "v2"):
                directory = REPOSITORY_ROOT / "runs" / model / f"run-{run_number:02d}" / version
                solution = directory / "solution.py"
                report = directory / "report.json"
                run([sys.executable, str(EVALUATOR), "--solution", str(solution), "--output", str(report), "--timeout", str(args.timeout)])
                if version == "v1":
                    run([sys.executable, str(FEEDBACK), "--report", str(report), "--output", str(directory / "feedback.txt")])
    return run([sys.executable, str(SUMMARY)])


if __name__ == "__main__":
    raise SystemExit(main())

