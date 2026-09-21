# LLM SSH Code Evaluation

Repositório do experimento independente **Comparação de LLMs na geração e correção automatizada de código para análise de logs SSH**.

## Resumo do experimento

O trabalho compara objetivamente três modelos de linguagem, de provedores distintos, na implementação de uma solução Python para analisar logs SSH e detectar possíveis tentativas de força bruta. Cada modelo foi executado com três níveis de raciocínio (`low`, `medium` e `high`). As soluções iniciais e as versões produzidas após feedback automático foram avaliadas pela mesma bateria de 20 testes determinísticos.

## Objetivo do artefato

Este repositório disponibiliza os prompts, dados sintéticos, soluções produzidas, implementação de referência, testes, avaliador e resultados estruturados necessários para inspecionar e reproduzir o experimento.

# Estrutura do README.md

Este README reúne as informações necessárias para compreender, executar e reproduzir o experimento. As seções apresentam:

1. ambiente e componentes do experimento;
2. dependências e precauções de execução;
3. instalação e teste mínimo;
4. reprodução e interpretação dos resultados;
5. licença.

O repositório está organizado da seguinte forma:

```text
llm-ssh-code-evaluation/
|-- data/
|   `-- samples/             # Logs SSH sintéticos de exemplo
|-- docs/
|   |-- PROTOCOLO.md         # Procedimento experimental congelado
|   |-- TESTES.md            # Catálogo dos 20 testes
|   `-- RELATORIO-RESULTADOS.md
|-- evaluator/
|   |-- evaluator.py         # Avaliação de uma solução
|   |-- worker.py            # Execução isolada de cada teste
|   |-- evaluate_all.py      # Reprodução completa das 18 avaliações
|   |-- generate_feedback.py # Feedback determinístico para as LLMs
|   `-- generate_summary.py  # Consolidação em JSON e CSV
|-- prompts/                 # Prompts inicial e de correção
|-- reference/solution.py    # Implementação usada para validar a bateria
|-- reports/                 # Relatórios auxiliares
|-- results/
|   |-- summary.csv          # Resultados tabulares
|   `-- summary.json         # Resultados e estatísticas estruturadas
|-- runs/                    # Soluções e relatórios dos modelos A, B e C
|-- tests/                   # Casos oficiais e testes da infraestrutura
|-- LICENSE
`-- README.md
```

A documentação metodológica detalhada está em [docs/PROTOCOLO.md](docs/PROTOCOLO.md), e a interpretação final está em [docs/RELATORIO-RESULTADOS.md](docs/RELATORIO-RESULTADOS.md).

# Informações básicas

## Ambiente de execução

| Componente | Requisito |
|---|---|
| Sistema operacional | Windows, Linux ou macOS |
| Python | 3.11 ou superior |
| Processador | 1 núcleo ou mais |
| Memória RAM | 256 MB livres ou mais |
| Espaço em disco | 10 MB livres ou mais |
| Rede | Necessária somente para clonar o repositório |
| Privilégios administrativos | Não são necessários |

O artefato foi validado em Windows com Python 3.14.6. O código utiliza apenas recursos compatíveis com Python 3.11 ou superior.

## Componentes principais

- `evaluator/evaluator.py`: recebe um `solution.py`, executa 20 testes e produz `report.json`.
- `evaluator/worker.py`: carrega a solução e executa cada teste em um subprocesso separado.
- `evaluator/evaluate_all.py`: avalia as 18 soluções existentes e regenera os resultados finais.
- `evaluator/generate_feedback.py`: converte um relatório em feedback textual determinístico.
- `evaluator/generate_summary.py`: calcula ganhos, correções, regressões e estatísticas por modelo.
- `tests/test_cases.py`: contém a bateria fixa de 20 casos.
- `tests/test_infrastructure.py`: verifica a referência e o tratamento de entregas ausentes.

## Convenção das execuções

| Diretório | Nível de raciocínio |
|---|---|
| `run-01` | low |
| `run-02` | medium |
| `run-03` | high |

Cada execução contém `v1`, correspondente à primeira entrega, e `v2`, correspondente à entrega posterior ao feedback automático.

# Dependências

O artefato não requer pacotes de terceiros. São utilizados somente módulos da biblioteca padrão do Python 3.11 ou superior.

Para verificar a versão instalada:

```powershell
python --version
```

Em sistemas nos quais o executável é chamado `python3`, substitua `python` por `python3` nos comandos.

Não são necessárias contas de provedores de LLM, chaves de API ou acesso aos serviços originais para reproduzir a avaliação. As 18 soluções coletadas já estão armazenadas em `runs/`.

# Preocupações com segurança

O avaliador executa arquivos Python gerados por modelos de linguagem. Cada teste roda em um subprocesso com limite de tempo, mas esse mecanismo **não constitui uma sandbox de sistema operacional**. O processo herda as permissões do usuário que executa o comando.

As soluções incluídas foram produzidas sob a restrição de usar apenas a biblioteca padrão e não acessar rede ou arquivos externos. Ainda assim, revisores que desejarem isolamento adicional devem executar o artefato em uma máquina virtual ou contêiner sem credenciais e sem dados pessoais montados.

O artefato:

- não requer privilégios administrativos;
- não modifica configurações do sistema;
- não necessita de credenciais;
- não envia dados pela rede durante os testes;
- grava somente os relatórios e resumos nos diretórios do próprio repositório.

# Instalação

## 1. Obter o repositório

```powershell
git clone https://github.com/Eduardo-Prates/llm-ssh-code-evaluation.git
cd llm-ssh-code-evaluation
```

Também é possível baixar o repositório como arquivo ZIP e extrair seu conteúdo.

## 2. Confirmar o ambiente

```powershell
python --version
```

O resultado deve indicar Python 3.11 ou superior. Não há etapa de instalação de dependências.

## 3. Verificar os arquivos essenciais

Confirme a presença dos seguintes caminhos:

```text
evaluator/evaluator.py
reference/solution.py
tests/test_cases.py
runs/model-a/run-01/v1/solution.py
results/summary.csv
```

Após essas etapas, o artefato está pronto para execução.

# Teste mínimo

O teste mínimo executa a bateria contra a implementação de referência.

## Comando

```powershell
python evaluator/evaluator.py --solution reference/solution.py --output reports/reference-report.json
```

## Tempo e recursos esperados

- tempo aproximado: 2 a 10 segundos;
- memória: menos de 256 MB;
- disco adicional: menos de 1 MB;
- rede: não utilizada.

## Resultado esperado

```text
Resultado: 20/20 testes; pontuação 100.00; delivery_error=false
```

O arquivo `reports/reference-report.json` será criado. Para validar também a infraestrutura:

```powershell
python -m unittest tests.test_infrastructure -v
```

O resultado esperado é `OK`, com dois testes aprovados.

# Experimentos

## Reprodução completa

Execute na raiz do repositório:

```powershell
python evaluator/evaluate_all.py
```

O script avalia, em sequência, as versões `v1` e `v2` das nove execuções, atualiza os relatórios individuais, gera os feedbacks das primeiras rodadas e reconstrói:

```text
results/summary.csv
results/summary.json
```

### Tempo e recursos esperados

- tempo aproximado: 15 a 60 segundos;
- memória: menos de 256 MB;
- disco adicional: menos de 5 MB;
- rede: não utilizada;
- execução: sequencial, com limite padrão de 3 segundos por teste.

Ao final, a mensagem esperada é:

```text
Resumo criado com 9 execução(ões)
```

Para visualizar os resultados:

```powershell
Import-Csv results/summary.csv | Format-Table
```

Em Linux ou macOS:

```bash
cat results/summary.csv
```

## Resultado 1 — Todas as soluções atendem aos requisitos avaliados

**Resultado observado:** as 18 soluções, considerando as versões iniciais e posteriores ao feedback, aprovam os 20 testes.

**Procedimento:** execute a reprodução completa e inspecione `results/summary.csv`.

**Resultado esperado:** as nove linhas devem apresentar:

```text
passed_v1 = 20
passed_v2 = 20
score_v1 = 100.0
score_v2 = 100.0
delivery_error_v1 = False
delivery_error_v2 = False
```

Isso corresponde a 360 aprovações em 360 execuções individuais de teste.

## Resultado 2 — O feedback não introduz regressões

**Resultado observado:** nenhuma solução posterior ao feedback perde um teste que era aprovado inicialmente.

**Procedimento:** após a reprodução completa, execute:

```powershell
Import-Csv results/summary.csv |
    Select-Object model, run, corrected_failures, regressions, regression_rate |
    Format-Table
```

**Resultado esperado:** `regressions` deve ser `0` e `regression_rate` deve ser `0.0` nas nove linhas. `corrected_failures` também será `0`, pois não ocorreram falhas iniciais. A taxa de correção permanece não aplicável.

Em Linux ou macOS, os mesmos valores podem ser conferidos diretamente em `results/summary.csv` ou `results/summary.json`.

## Resultado 3 — Não houve diferença observável entre os níveis de raciocínio

**Resultado observado:** low, medium e high produziram os mesmos resultados nesta tarefa.

**Procedimento:** relacione `run-01`, `run-02` e `run-03` conforme a convenção apresentada em “Informações básicas” e compare `score_v1` e `score_v2`.

**Resultado esperado:** todas as pontuações devem ser iguais a 100, com desvio-padrão igual a 0 para cada modelo.

Esse resultado caracteriza um efeito teto. Ele não demonstra equivalência geral entre modelos ou níveis de raciocínio; indica apenas que a tarefa e a bateria utilizadas não produziram diferenças mensuráveis.

## Rastreabilidade dos resultados

| Resultado | Evidência principal | Documentação |
|---|---|---|
| 1. Aprovação integral | `results/summary.csv` | [Relatório, seções 3 e 4](docs/RELATORIO-RESULTADOS.md) |
| 2. Ausência de regressões | campos `regressions` e `regression_rate` | [Relatório, seção 5](docs/RELATORIO-RESULTADOS.md) |
| 3. Igualdade observada entre níveis | estatísticas em `results/summary.json` | [Relatório, seções 6 e 7](docs/RELATORIO-RESULTADOS.md) |

Os prompts, testes e critérios empregados estão documentados em [docs/PROTOCOLO.md](docs/PROTOCOLO.md) e [docs/TESTES.md](docs/TESTES.md).

# LICENSE

Este artefato é disponibilizado sob a licença MIT. Consulte o arquivo [LICENSE](LICENSE) para o texto completo.
