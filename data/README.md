# Dados do experimento

Os arquivos em `samples/` contêm somente dados sintéticos. Nenhuma linha foi obtida de sistemas reais.

- `sample-valid.log`: exemplos válidos de falha, autenticação aceita e IPv6.
- `sample-brute-force.log`: cinco falhas do mesmo IP no limite inclusivo de 60 segundos.
- `sample-mixed.log`: mistura de linhas válidas, aceitas, vazias, desconhecidas e malformadas.

Esses arquivos servem para demonstração e documentação. A pontuação oficial é determinada exclusivamente pelos casos definidos em `tests/test_cases.py`.

