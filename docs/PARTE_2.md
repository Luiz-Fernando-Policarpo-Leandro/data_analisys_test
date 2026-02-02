# Parte 2 – Transformação, Validação e Enriquecimento de Dados

Este documento descreve as decisões técnicas, estratégias adotadas e trade-offs
considerados na implementação da **Parte 2 do desafio**, que envolve validação,
enriquecimento e agregação dos dados consolidados de despesas da ANS.

---

## 2.1 Validação de Dados com Estratégias Diferentes

### Regras aplicadas

Foram implementadas as seguintes validações sobre o CSV consolidado da Parte 1:

- **CNPJ válido**
  - Validação de formato
  - Validação de dígitos verificadores
- **Valores numéricos positivos**
- **Razão Social não vazia**

### Estratégia adotada para CNPJs inválidos

Os registros com CNPJ inválido **não são descartados silenciosamente**.
Eles são classificados e segregados em arquivos específicos.

#### Justificativa (trade-off)

**Prós**
- Preserva rastreabilidade e auditabilidade
- Permite análise posterior de inconsistências na fonte
- Evita perda de dados potencialmente relevantes

**Contras**
- Aumenta o número de artefatos gerados
- Exige lógica adicional de classificação

Essa abordagem foi escolhida por privilegiar **integridade analítica** em vez de
simplicidade operacional.

---

## 2.2 Enriquecimento de Dados com Tratamento de Falhas

### Fonte de dados cadastrais

Os dados cadastrais das operadoras ativas foram obtidos a partir do repositório
oficial da ANS:

https://dadosabertos.ans.gov.br/FTP/PDA/operadoras_de_plano_de_saude_ativas/

O download é realizado automaticamente durante a execução do pipeline.

---

### Estratégia de join

O enriquecimento é realizado via **join entre os dados consolidados de despesas e
o cadastro oficial**, utilizando **CNPJ como chave primária**.

As seguintes colunas são adicionadas ao dataset final:
- `RegistroANS`
- `Modalidade`
- `UF`

---

### Tratamento de registros sem correspondência

Durante a análise exploratória, observou-se que:
- Alguns CNPJs presentes no consolidado não existem no cadastro ativo
- Alguns CNPJs aparecem múltiplas vezes no cadastro com dados divergentes

#### Decisões adotadas

- Registros **sem match no cadastro** são mantidos, com campos cadastrais nulos
- Em caso de múltiplos registros no cadastro:
  - É mantido um único registro por CNPJ
  - Prioriza-se consistência estrutural em vez de heurísticas arbitrárias

#### Justificativa (trade-off)

Essa abordagem evita:
- Exclusão indevida de despesas válidas
- Introdução de regras subjetivas difíceis de justificar tecnicamente

---

## 2.3 Agregação com Múltiplas Estratégias

### Estratégia de agrupamento

Os dados foram agregados considerando as seguintes dimensões:
- `RazaoSocial`
- `UF`
- `RegistroANS`
- `CNPJ`
- `Ano`

Embora o enunciado mencione agregação apenas por RazaoSocial e UF, optou-se por
manter também RegistroANS e CNPJ no agrupamento.

### Justificativa técnica

Na análise exploratória dos dados, observou-se uma relação prática **1:1 entre
RazaoSocial, CNPJ e RegistroANS** para o período analisado.

A manutenção dessas chaves:
- Preserva integridade regulatória
- Evita agregações indevidas em casos de homônimos
- Mantém rastreabilidade histórica em cenários de alteração societária

---

### Métricas calculadas

Para cada grupo foram calculados:
- **Total de despesas**
- **Média trimestral de despesas**
- **Desvio padrão das despesas**

Essas métricas permitem identificar:
- Operadoras com maior impacto financeiro
- Comportamentos médios ao longo do tempo
- Alta variabilidade de despesas (outliers operacionais)

---

## Estratégia de ordenação

A ordenação dos resultados foi realizada em memória utilizando o método
`sort_values` do Pandas, após a etapa de agregação dos dados.

### Justificativa técnica

- A ordenação é aplicada somente após a agregação anual das despesas,
  reduzindo significativamente o volume de dados a ser ordenado.
- O volume final (operadoras × anos) é pequeno o suficiente para ser
  processado em memória sem impacto relevante de desempenho.
- O Pandas utiliza o algoritmo **Timsort**, eficiente para datasets
  parcialmente ordenados, com complexidade O(n log n) no pior caso.
- Essa abordagem reduz a complexidade da solução e evita o uso
  desnecessário de frameworks distribuídos ou múltiplos passes de dados.

Caso o volume de dados cresça significativamente no futuro, a ordenação
poderia ser delegada a um banco de dados analítico ou a processamento
distribuído.

---

## Entrega final

O resultado da Parte 2 é salvo no arquivo:

- `despesas_agregadas.csv`

Conforme solicitado no enunciado, o conjunto de arquivos gerados é
compactado em um único arquivo ZIP para entrega.

---

## Considerações finais

As decisões técnicas desta etapa priorizaram:
- Clareza de regras
- Rastreabilidade dos dados
- Justificativas objetivas para cada trade-off
- Aderência ao escopo do desafio sem overengineering

