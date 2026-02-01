# Parte 1 — Download, Extração e Normalização dos Dados da ANS

Este documento descreve **em nível técnico** como a Parte 1 do projeto foi implementada: da descoberta dos arquivos públicos da ANS até a geração de dados normalizados prontos para consolidação.

O objetivo aqui **não é repetir o código**, mas explicar **as decisões técnicas, o fluxo de dados e os trade-offs** adotados.

---

## Objetivo da Parte 1

A Parte 1 resolve os seguintes problemas:

* Descobrir automaticamente os arquivos disponíveis no repositório público da ANS
* Organizar os arquivos por **ano e trimestre**
* Selecionar apenas os **3 últimos trimestres de cada ano**
* Fazer download eficiente e resiliente dos arquivos
* Extrair conteúdos compactados
* Normalizar estruturas heterogêneas de dados
* Produzir DataFrames consistentes para consolidação posterior

Essa etapa **não toma decisões de negócio finais**, apenas prepara dados confiáveis.

---

## Descoberta dos arquivos (listagem dinâmica)

A ANS disponibiliza os arquivos em um repositório HTTP estruturado por pastas.

A aplicação:

1. Faz requisição HTTP para a URL base
2. Usa `BeautifulSoup` para parsear o HTML
3. Extrai apenas links relevantes (`.zip`)
4. Ignora diretórios e arquivos fora do padrão esperado

### Motivo da escolha

* O FTP **não possui API oficial**
* Scraping controlado é a única forma confiável
* Evita hardcode de anos ou trimestres

Trade-off: depende da estabilidade do HTML da ANS (aceitável para dados públicos).

---

## Extração de ano e trimestre

Cada arquivo contém informações temporais embutidas no nome.

Foi utilizado **regex** para extrair:

* Ano (YYYY)
* Trimestre (1–4)

Esses metadados são armazenados junto com o arquivo antes do download.

### Por que não inferir depois?

* Nem todos os arquivos possuem campos confiáveis de ano/trimestre
* O nome do arquivo é a fonte mais consistente

---

## Seleção dos 3 últimos trimestres por ano

Após listar todos os arquivos:

1. Os arquivos são agrupados por ano
2. Cada grupo é ordenado por trimestre
3. Apenas os **3 últimos** são mantidos

Isso garante:

* Cobertura completa de múltiplos anos
* Evita misturar períodos incompletos
* Cumpre exatamente o requisito do desafio

---

## Download eficiente (I/O bound)

O download é feito usando `ThreadPoolExecutor`.

Justificativa:

* Download é operação I/O bound
* Threads são mais eficientes que processos nesse cenário
* Reduz drasticamente o tempo total de execução

Cada arquivo é baixado apenas **uma vez**.

### Idempotência

Se `consolidado_despesas.csv` já existir:

* O pipeline ignora o download
* Usa o arquivo local diretamente

Isso permite reexecução segura.

---

## Extração de arquivos compactados

Os arquivos da ANS são fornecidos em ZIP.

Fluxo:

1. ZIP é aberto em diretório temporário
2. Cada arquivo interno é processado individualmente
3. O diretório temporário é removido após uso

Motivo:

* Evita poluir o projeto
* Reduz risco de conflito de nomes

---

## Leitura de múltiplos formatos

Os arquivos internos podem ser:

* CSV
* TXT delimitado
* XLS / XLSX

A leitura é feita de forma defensiva:

* Detecção automática do separador
* Fallbacks para encoding
* Conversão para `pandas.DataFrame`

Trade-off: maior complexidade, porém maior robustez.

---

## Normalização dos dados

Todos os DataFrames são normalizados para conter, no mínimo:

* REG_ANS
* CNPJ
* Razão Social
* Ano
* Trimestre
* Valor

### Estratégias adotadas

* Renomeação de colunas inconsistentes
* Criação de colunas ausentes
* Padronização de tipos

Colunas de ano e trimestre utilizam `Int64` (nullable), evitando erros de casting.

---

## Paralelismo no processamento (CPU bound)

A leitura e normalização dos arquivos extraídos é feita com `ProcessPoolExecutor`.

Motivo:

* Parsing e limpeza de dados é CPU bound
* Processos evitam o GIL do Python

Resultado:

* Melhor escalabilidade
* Processamento mais previsível

---

## Saída da Parte 1

Ao final da Parte 1, o sistema produz:

* Um conjunto de DataFrames homogêneos
* Metadados temporais confiáveis
* Dados prontos para validação e consolidação

Nenhuma regra de negócio definitiva é aplicada aqui.

---

## Limitações conhecidas

* Dependência do layout HTML da ANS
* Arquivos com formatação inconsistente exigem fallback
* Não há cache intermediário de arquivos individuais

Essas limitações são aceitáveis para o escopo do desafio.

---

## Conclusão

A Parte 1 prioriza:

* Automação completa
* Robustez contra inconsistências
* Clareza no fluxo de dados

Ela estabelece uma base sólida para a **Parte 2**, onde entram as validações contábeis e regras de negócio.
