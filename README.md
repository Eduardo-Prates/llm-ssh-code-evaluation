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
- somente dependências documentadas pelo avaliador;
- os mesmos comandos, dados e limites de execução para todos os modelos.

Os comandos definitivos de instalação e avaliação serão adicionados quando o avaliador automatizado estiver concluído.

## Reprodutibilidade

Durante a coleta, os prompts, os testes e as regras de pontuação devem permanecer congelados. Cada execução deve registrar o modelo, o provedor, a versão exibida, a forma de acesso, as configurações disponíveis e a data da geração.

Os testes podem permanecer reservados durante o experimento e ser publicados após a conclusão das execuções.

## Estado do projeto

O repositório está em preparação. A estrutura experimental foi criada e os próximos passos são adicionar o protocolo, os prompts, o avaliador, a implementação de referência e a bateria de testes.

## Licença

Consulte o arquivo [LICENSE](LICENSE).
