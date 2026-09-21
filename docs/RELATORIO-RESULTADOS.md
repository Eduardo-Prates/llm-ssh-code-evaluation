# Relatório de resultados

## 1. Finalidade

Este documento apresenta os resultados da aplicação do protocolo experimental para comparação de três modelos de linguagem na geração e revisão de uma solução Python para análise de logs SSH.

O protocolo metodológico permanece registrado em [PROTOCOLO.md](PROTOCOLO.md). Os resultados estruturados utilizados neste relatório estão disponíveis em [`results/summary.csv`](../results/summary.csv) e [`results/summary.json`](../results/summary.json).

## 2. Desenho executado

Foram avaliados três modelos, identificados como `model-a`, `model-b` e `model-c`. Cada modelo foi executado em três níveis de raciocínio:

| Execução | Nível |
|---|---|
| `run-01` | low |
| `run-02` | medium |
| `run-03` | high |

Cada execução produziu uma solução inicial (`v1`) e uma solução posterior ao feedback automático (`v2`). Cada solução foi submetida à mesma bateria de 20 testes determinísticos.

O conjunto final contém:

- 3 modelos;
- 3 execuções por modelo;
- 9 pares de execução;
- 18 soluções avaliadas;
- 20 testes por solução;
- 360 resultados individuais de teste.

## 3. Resultados por execução

| Modelo | Nível | V1 | V2 | Ganho | Falhas corrigidas | Regressões | Erro de entrega |
|---|---|---:|---:|---:|---:|---:|---|
| model-a | low | 20/20 | 20/20 | 0 | 0 | 0 | não |
| model-a | medium | 20/20 | 20/20 | 0 | 0 | 0 | não |
| model-a | high | 20/20 | 20/20 | 0 | 0 | 0 | não |
| model-b | low | 20/20 | 20/20 | 0 | 0 | 0 | não |
| model-b | medium | 20/20 | 20/20 | 0 | 0 | 0 | não |
| model-b | high | 20/20 | 20/20 | 0 | 0 | 0 | não |
| model-c | low | 20/20 | 20/20 | 0 | 0 | 0 | não |
| model-c | medium | 20/20 | 20/20 | 0 | 0 | 0 | não |
| model-c | high | 20/20 | 20/20 | 0 | 0 | 0 | não |

Todas as 18 soluções foram entregues corretamente e aprovadas nos 20 testes.

## 4. Resultados consolidados

| Modelo | Média V1 | Mediana V1 | Média V2 | Mediana V2 | Desvio-padrão | Regressões |
|---|---:|---:|---:|---:|---:|---:|
| model-a | 100 | 100 | 100 | 100 | 0 | 0 |
| model-b | 100 | 100 | 100 | 100 | 0 | 0 |
| model-c | 100 | 100 | 100 | 100 | 0 | 0 |

Em todos os modelos, o mínimo e o máximo das pontuações inicial e final foram iguais a 100. Não houve variação entre as três execuções de cada modelo.

A taxa de correção é não aplicável, pois nenhuma execução apresentou falhas na primeira rodada. A taxa de regressão foi igual a 0% em todas as execuções.

## 5. Respostas às questões de pesquisa

### QP1 — Qual modelo aprovou mais testes na primeira tentativa?

Os três modelos ficaram empatados. Todos aprovaram 20 de 20 testes nas três execuções iniciais.

### QP2 — Qual modelo corrigiu a maior proporção das falhas?

Não foi possível comparar a capacidade de correção. Nenhuma solução apresentou falhas na primeira rodada, portanto não existiam falhas que pudessem ser corrigidas.

### QP3 — Quais modelos introduziram regressões durante a correção?

Nenhum modelo introduziu regressões. Todas as soluções `v2` preservaram os 20 testes que já eram aprovados em `v1`.

### QP4 — Qual modelo alcançou o melhor resultado final?

Os três modelos ficaram empatados com pontuação final igual a 100 em todas as execuções.

## 6. Efeito dos níveis de raciocínio

Não foi observada diferença mensurável entre low, medium e high. Todos os níveis produziram pontuação inicial e final igual a 100.

Esse resultado significa apenas que o nível de raciocínio não alterou o desempenho observado nesta tarefa e nesta bateria de testes. Ele não demonstra equivalência geral entre os níveis em tarefas mais complexas.

## 7. Discussão

Os resultados confirmam que os três modelos foram capazes de implementar integralmente os comportamentos verificados pela bateria. A manutenção dos 20 testes aprovados após o feedback também demonstra estabilidade nas soluções revisadas.

Entretanto, ocorreu um efeito teto: todos os participantes atingiram a pontuação máxima desde a primeira tentativa. Consequentemente, a tarefa não forneceu variação suficiente para ordenar os modelos ou avaliar comparativamente sua capacidade de corrigir falhas.

O empate não deve ser interpretado como evidência de que os modelos possuem capacidades gerais equivalentes. A conclusão válida é mais restrita: para a especificação, os prompts, as configurações e os testes utilizados, todos atenderam integralmente aos requisitos avaliados.

## 8. Limitações

- O experimento utilizou uma única tarefa de programação.
- A bateria contém 20 testes e cobre somente os comportamentos previstos no protocolo.
- Todos os participantes alcançaram a pontuação máxima, limitando o poder discriminativo.
- A capacidade de correção não pôde ser medida porque não ocorreram falhas iniciais.
- Os identificadores `model-a`, `model-b` e `model-c` não descrevem, por si só, versões ou configurações dos provedores.
- Os resultados não devem ser generalizados para outras tarefas, linguagens ou contextos.

## 9. Conclusão

As nove execuções iniciais e as nove execuções posteriores ao feedback foram concluídas sem erros de entrega. Todas as 18 soluções aprovaram os 20 testes, totalizando 360 aprovações em 360 avaliações individuais.

Não foram identificadas diferenças entre modelos ou níveis de raciocínio, e nenhuma regressão foi introduzida. O experimento demonstrou sucesso uniforme na tarefa proposta, mas não permitiu estabelecer um vencedor.

Uma avaliação futura que busque diferenciar os participantes deverá ser registrada como uma nova versão do protocolo e executada novamente para todos os modelos. A versão atual e seus resultados devem ser preservados sem alterações retrospectivas nos prompts, testes ou critérios de pontuação.

## 10. Reprodução

Para regenerar todos os relatórios e a consolidação:

```powershell
python evaluator/evaluate_all.py
```

Para verificar a infraestrutura do avaliador:

```powershell
python -m unittest tests.test_infrastructure -v
```
