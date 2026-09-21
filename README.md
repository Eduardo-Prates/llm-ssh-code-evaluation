# LLM SSH Code Evaluation

Experimento reprodutível para comparar três modelos de linguagem, de três provedores diferentes, na geração e correção de código Python para análise de logs SSH.

## Objetivo

Avaliar objetivamente a capacidade dos modelos de:

- implementar uma solução a partir da mesma especificação;
- produzir um arquivo Python executável;
- interpretar um relatório automático de testes;
- corrigir falhas sem intervenção humana no código;
- preservar funcionalidades que já estavam corretas.

A tarefa consiste em implementar um analisador simplificado de logs SSH capaz de identificar possíveis tentativas de força bruta dentro de uma janela móvel de tempo.

## Desenho experimental

O experimento utiliza:

- três LLMs de provedores diferentes;
- três execuções independentes por modelo;
- uma solução inicial (`v1`) e uma solução corrigida (`v2`) por execução;
- o mesmo prompt para todos os modelos;
- uma bateria fixa de 20 testes determinísticos;
- uma única oportunidade de correção após o feedback automático.

Isso resulta em nove soluções iniciais e nove soluções corrigidas.

## Fluxo de cada execução

1. Iniciar uma conversa nova com o modelo.
2. Enviar o prompt inicial sem modificações.
3. Baixar o arquivo `solution.py` entregue pelo modelo.
4. Salvar o arquivo sem copiar, reformatar ou corrigir seu conteúdo.
5. Executar a bateria padronizada de testes.
6. Gerar o relatório automático da primeira rodada.
7. Enviar ao modelo a especificação original, sua solução anterior e o relatório automático.
8. Baixar o novo arquivo `solution.py`.
9. Executar novamente a mesma bateria de testes.
10. Gerar e consolidar as métricas finais.

Se a interface não fornecer um arquivo baixável chamado `solution.py`, a ocorrência deve ser registrada como `delivery_error`. O arquivo não deve ser reconstruído manualmente a partir do texto da conversa.

## Estrutura do repositório

```text
llm-ssh-code-evaluation/
|-- data/
|   `-- samples/             # Dados sintéticos usados no experimento
|-- docs/                    # Protocolo e documentação metodológica
|-- evaluator/               # Avaliador e geradores de relatórios
|-- prompts/                 # Prompts inicial e de correção
|-- reference/               # Implementação de referência
|-- reports/                 # Relatórios consolidados
|-- results/                 # Tabelas e métricas finais
|-- runs/
|   |-- model-a/
|   |-- model-b/
|   `-- model-c/
|       |-- run-01/
|       |   |-- v1/         # Primeira solução
|       |   `-- v2/         # Solução após o feedback
|       |-- run-02/
|       `-- run-03/
|-- tests/                   # Bateria padronizada de testes
|-- LICENSE
`-- README.md
```

Cada pasta `v1` ou `v2` poderá conter:

```text
solution.py       # Arquivo entregue diretamente pelo modelo
report.json       # Resultado produzido pelo avaliador
metadata.json     # Modelo, provedor, versão e configurações
raw-response.txt  # Registro da conversa, quando permitido
```

## Critérios de avaliação

Somente resultados verificáveis automaticamente serão considerados:

- quantidade de testes aprovados na primeira rodada;
- quantidade de testes aprovados após a correção;
- pontuação inicial e final;
- falhas corrigidas;
- regressões introduzidas;
- ganho absoluto de testes;
- taxa de correção;
- taxa de regressão;
- erro de entrega do arquivo.

Aspectos subjetivos, como estilo do código, qualidade da explicação ou preferência dos avaliadores, não serão pontuados.

## Requisitos do ambiente

- Python 3.11 ou superior;
- nenhuma biblioteca externa obrigatória;
- os mesmos comandos, dados e limites de execução para todos os modelos.

## Execução rápida

Valide a infraestrutura usando a implementação de referência:

```powershell
python evaluator/evaluator.py --solution reference/solution.py --output reports/reference-report.json
```

Gere o feedback determinístico de uma execução:

```powershell
python evaluator/generate_feedback.py --report reports/reference-report.json --output reports/reference-feedback.txt
```

Avalie todas as pastas previstas no protocolo e consolide os resultados:

```powershell
python evaluator/evaluate_all.py
```

Os comandos podem ser executados da mesma forma no Linux ou no macOS, substituindo `python` por `python3` quando necessário. Consulte [docs/PROTOCOLO.md](docs/PROTOCOLO.md) para o procedimento completo.

## Resultados finais

As nove execuções foram concluídas. Os três modelos, nos níveis low, medium e high, aprovaram os 20 testes tanto na primeira entrega quanto após o feedback. Não ocorreram erros de entrega ou regressões.

O resultado produziu um efeito teto: a tarefa confirmou que todos os participantes atendem integralmente aos requisitos avaliados, mas não permitiu diferenciá-los.

- [Relatório completo dos resultados](docs/RELATORIO-RESULTADOS.md)
- [Resultados em CSV](results/summary.csv)
- [Resultados em JSON](results/summary.json)

## Reprodutibilidade

Durante a coleta, os prompts, os testes e as regras de pontuação devem permanecer congelados. Cada execução deve registrar o modelo, o provedor, a versão exibida, a forma de acesso, as configurações disponíveis e a data da geração.

Os testes podem permanecer reservados durante o experimento e ser publicados após a conclusão das execuções.

## Estado do projeto

O experimento está concluído. O repositório contém o protocolo, os prompts utilizados, os dados sintéticos, a implementação de referência, a bateria de 20 testes, as 18 soluções avaliadas, os relatórios automáticos e a consolidação final das métricas.

## Licença

Consulte o arquivo [LICENSE](LICENSE).
