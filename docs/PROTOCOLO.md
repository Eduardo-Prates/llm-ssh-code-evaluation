# Protocolo operacional

## Preparação

1. Use Python 3.11 ou superior.
2. Não altere os arquivos em `prompts/` ou `tests/` depois do início da coleta.
3. Valide o avaliador com a implementação de referência:

```powershell
python evaluator/evaluator.py --solution reference/solution.py --output reports/reference-report.json
```

O comando deve encerrar com código zero e informar 20 testes aprovados.

## Primeira rodada

1. Abra uma conversa nova com o modelo.
2. Envie `prompts/prompt-inicial.txt` sem modificações.
3. Baixe `solution.py` diretamente da interface.
4. Salve-o em `runs/model-x/run-yy/v1/solution.py` sem alterar seu conteúdo.
5. Copie `docs/metadata-template.json` para a mesma pasta como `metadata.json` e preencha os campos.
6. Execute:

```powershell
python evaluator/evaluator.py --solution runs/model-a/run-01/v1/solution.py --output runs/model-a/run-01/v1/report.json
python evaluator/generate_feedback.py --report runs/model-a/run-01/v1/report.json --output runs/model-a/run-01/v1/feedback.txt
```

Se não houver arquivo baixável, execute o avaliador apontando para o caminho esperado. Ele criará um relatório com `delivery_error: true`.

## Rodada de correção

1. Envie a especificação original, o código anterior, o conteúdo de `feedback.txt` e `prompts/prompt-correcao.txt`.
2. Baixe o novo `solution.py` e salve-o em `v2/` sem alterações.
3. Repita a avaliação usando o caminho de `v2`.

## Execução em lote

Para avaliar todos os 18 espaços esperados, inclusive entregas ausentes:

```powershell
python evaluator/evaluate_all.py
```

Para consolidar as métricas novamente:

```powershell
python evaluator/generate_summary.py
```

Os resultados consolidados são gravados em `results/summary.json` e `results/summary.csv`.

