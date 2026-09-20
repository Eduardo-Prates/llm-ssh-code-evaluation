from __future__ import annotations

import argparse
import json
from pathlib import Path


def build_feedback(report: dict) -> str:
    lines = [
        "RELATÓRIO AUTOMÁTICO DE TESTES",
        "",
        f"Versão do protocolo: {report.get('protocol_version', 'desconhecida')}",
        f"Testes aprovados: {report.get('passed', 0)}/{report.get('total', 0)}",
        f"Pontuação: {report.get('score', 0)}",
        f"Erro de entrega: {str(bool(report.get('delivery_error'))).lower()}",
        "",
    ]
    failed = [test for test in report.get("tests", []) if test.get("status") != "passed"]
    if not failed:
        lines.append("Todos os testes foram aprovados.")
        return "\n".join(lines) + "\n"

    lines.append("TESTES QUE FALHARAM")
    lines.append("")
    for test in failed:
        lines.append(f"{test.get('id')} - {test.get('name')}")
        lines.append(f"grupo: {test.get('group')}")
        lines.append(f"erro: {test.get('error_type', 'falha de asserção')}")
        if "expected" in test:
            lines.append(f"esperado: {test['expected']}")
        if "actual" in test:
            lines.append(f"obtido: {test['actual']}")
        if test.get("message"):
            lines.append(f"mensagem: {test['message']}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Converte report.json em feedback determinístico")
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    report = json.loads(args.report.read_text(encoding="utf-8"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(build_feedback(report), encoding="utf-8")
    print(f"Feedback salvo em {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

