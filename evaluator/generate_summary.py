from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from statistics import mean, median, pstdev


def load_reports(runs_root: Path) -> dict[tuple[str, str, str], dict]:
    reports = {}
    for path in sorted(runs_root.glob("*/run-*/v*/report.json")):
        relative = path.relative_to(runs_root)
        model, run_id, version = relative.parts[:3]
        reports[(model, run_id, version)] = json.loads(path.read_text(encoding="utf-8"))
    return reports


def passed_ids(report: dict | None) -> set[str]:
    if report is None:
        return set()
    return {test["id"] for test in report.get("tests", []) if test.get("status") == "passed"}


def round_metrics(model: str, run_id: str, v1: dict | None, v2: dict | None) -> dict:
    total = (v1 or v2 or {}).get("total", 20)
    v1_passed = passed_ids(v1)
    v2_passed = passed_ids(v2)
    p1 = len(v1_passed)
    p2 = len(v2_passed)
    corrected = len(v2_passed - v1_passed)
    regressions = len(v1_passed - v2_passed)
    initial_failures = total - p1
    return {
        "model": model,
        "run": run_id,
        "total": total,
        "passed_v1": p1,
        "passed_v2": p2,
        "score_v1": round(p1 / total * 100, 2),
        "score_v2": round(p2 / total * 100, 2),
        "absolute_gain": p2 - p1,
        "corrected_failures": corrected,
        "regressions": regressions,
        "correction_rate": None if initial_failures == 0 else round(corrected / initial_failures * 100, 2),
        "regression_rate": None if p1 == 0 else round(regressions / p1 * 100, 2),
        "delivery_error_v1": True if v1 is None else bool(v1.get("delivery_error")),
        "delivery_error_v2": True if v2 is None else bool(v2.get("delivery_error")),
    }


def statistics_for(values: list[float]) -> dict | None:
    if not values:
        return None
    return {
        "mean": round(mean(values), 2),
        "median": round(median(values), 2),
        "minimum": round(min(values), 2),
        "maximum": round(max(values), 2),
        "population_standard_deviation": round(pstdev(values), 2),
    }


def aggregate(rows: list[dict]) -> dict:
    by_model = {}
    numeric_fields = ["passed_v1", "passed_v2", "score_v1", "score_v2", "absolute_gain", "corrected_failures", "regressions", "correction_rate", "regression_rate"]
    for model in sorted({row["model"] for row in rows}):
        model_rows = [row for row in rows if row["model"] == model]
        by_model[model] = {
            field: statistics_for([row[field] for row in model_rows if row[field] is not None])
            for field in numeric_fields
        }
        by_model[model]["runs"] = len(model_rows)
    return by_model


def write_csv(rows: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0]) if rows else ["model", "run"]
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="Consolida os relatórios das duas rodadas")
    parser.add_argument("--runs-root", type=Path, default=Path("runs"))
    parser.add_argument("--json-output", type=Path, default=Path("results/summary.json"))
    parser.add_argument("--csv-output", type=Path, default=Path("results/summary.csv"))
    args = parser.parse_args()
    reports = load_reports(args.runs_root)
    pairs = sorted({(model, run_id) for model, run_id, _ in reports})
    rows = [round_metrics(model, run_id, reports.get((model, run_id, "v1")), reports.get((model, run_id, "v2"))) for model, run_id in pairs]
    payload = {"runs": rows, "by_model": aggregate(rows)}
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_csv(rows, args.csv_output)
    print(f"Resumo criado com {len(rows)} execução(ões)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

