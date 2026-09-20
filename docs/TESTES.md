# Catálogo da bateria padronizada

Cada teste vale cinco pontos. A bateria totaliza 100 pontos e não utiliza aleatoriedade.

| ID | Grupo | Comportamento verificado |
|---|---|---|
| T01 | Parser | Falha para usuário existente |
| T02 | Parser | Falha contendo `invalid user` |
| T03 | Parser | Autenticação aceita retorna `None` |
| T04 | Parser | Linha malformada retorna `None` |
| T05 | Parser | Linha não relacionada retorna `None` |
| T06 | Parser | Endereço IPv6 |
| T07 | Detecção | Cinco falhas em menos de 60 segundos |
| T08 | Detecção | Cinco falhas em mais de 60 segundos |
| T09 | Detecção | Limite inclusivo de exatamente 60 segundos |
| T10 | Detecção | Eventos recebidos fora de ordem |
| T11 | Detecção | Dois endereços IP diferentes |
| T12 | Detecção | Somente o primeiro alerta por IP |
| T13 | Detecção | Usuários únicos em ordem alfabética |
| T14 | Detecção | `threshold` personalizado |
| T15 | Detecção | `window_seconds` personalizado |
| T16 | Detecção | `threshold` igual a 1 |
| T17 | Saída | Ordenação dos alertas por `start` e `ip` |
| T18 | Saída | Campos exatos, tipos e formato ISO |
| T19 | Robustez | Lista de entrada vazia |
| T20 | Robustez | Mistura de linhas válidas, inválidas e irrelevantes |

Os testes são executados separadamente em subprocessos. O tempo padrão máximo é de três segundos para cada caso.
