## Estratégia de ordenação

A ordenação dos resultados foi realizada em memória utilizando o método
`sort_values` do Pandas, após a etapa de agregação dos dados.

### Justificativa técnica

- A ordenação é aplicada somente após a agregação anual das despesas,
  reduzindo significativamente o volume de dados a ser ordenado.
- O volume final (operadoras × anos) é pequeno o suficiente para ser
  processado em memória sem impacto relevante de desempenho.
- O Pandas utiliza o algoritmo Timsort, eficiente para datasets parcialmente
  ordenados e com complexidade O(n log n) no pior caso.
- Essa abordagem reduz a complexidade da solução e evita o uso desnecessário
  de frameworks distribuídos ou processamento em múltiplos passes.

Caso o volume de dados cresça significativamente no futuro, a ordenação poderia
ser delegada a um banco de dados analítico ou realizada em processamento
distribuído.



Embora o enunciado mencione agregação por RazaoSocial e UF, optou-se por manter também RegistroANS e CNPJ no agrupamento. Na análise exploratória dos dados observou-se uma relação 1:1 entre RazaoSocial, CNPJ e RegistroANS para o período analisado, o que elimina duplicidade prática. A decisão preserva integridade regulatória, rastreabilidade e evita agregações indevidas em casos de homônimos ou alterações societárias.

