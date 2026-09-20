from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
EVALUATOR = ROOT / "evaluator" / "evaluator.py"
REFERENCE = ROOT / "reference" / "solution.py"


class InfrastructureTests(unittest.TestCase):
    def run_evaluator(self, solution: Path) -> tuple[subprocess.CompletedProcess[str], dict]:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "report.json"
            completed = subprocess.run(
                [sys.executable, str(EVALUATOR), "--solution", str(solution), "--output", str(output)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )
            report = json.loads(output.read_text(encoding="utf-8"))
        return completed, report

    def test_reference_passes_all_twenty_tests(self) -> None:
        completed, report = self.run_evaluator(REFERENCE)
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertEqual(report["passed"], 20)
        self.assertEqual(report["failed"], 0)
        self.assertFalse(report["delivery_error"])

    def test_missing_solution_is_delivery_error(self) -> None:
        completed, report = self.run_evaluator(ROOT / "solution.py")
        self.assertEqual(completed.returncode, 2)
        self.assertTrue(report["delivery_error"])
        self.assertEqual(report["passed"], 0)
        self.assertEqual(report["failed"], 20)


if __name__ == "__main__":
    unittest.main()
