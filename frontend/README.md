# Frontend – Interface de Operadoras e Estatísticas (Vue.js)

Esta seção do projeto compreende a interface web desenvolvida para interagir com o servidor FastAPI, permitindo a visualização, busca e análise detalhada dos dados das operadoras da ANS.

## Estrutura de Arquivos

frontend/
├── src/
│ ├── api/
│ │ └── http.ts # Configuração do Axios e URL base da API
│ ├── components/
│ │ ├── DespesasChart.vue # Componente de gráfico (Chart.js/ApexCharts)
│ │ └── OperadorasTable.vue # Tabela de listagem reaproveitável
│ ├── composables/
│ │ └── useOperadoras.ts # Lógica de estado e busca (Vue 3 Composables)
│ ├── views/
│ │ ├── OperadorasList.vue # Página principal com busca e paginação
│ │ ├── OperadoraDetalhe.vue# Detalhes e métricas (abre em nova aba)
│ │ └── Estatisticas.vue # Dashboard global e Top 5 operadoras
│ ├── router/
│ │ └── index.ts # Configuração das rotas (Vue Router)
│ ├── App.vue # Componente raiz
│ └── main.ts # Inicialização do Vue
├── package.json # Dependências (Vue 3, Vite, Axios)
└── README.md # Documentação específica do frontend


## Justificativas Técnicas (Trade-offs)

### 1. Gerenciamento de Estado: Composables (Vue 3)

- **Escolha:** Composables
- **Justificativa:** Para uma aplicação de escopo focado, o uso de composables (`useOperadoras.ts`) oferece simplicidade e organização. Ele encapsula a lógica de busca e paginação de forma reativa, sem a complexidade de um store global como Vuex ou Pinia, que seria excessivo para este volume de dados.

### 2. Estratégia de Busca e Filtro: Híbrida

- **Escolha:** Híbrido
- **Justificativa:** A busca inicial é realizada no servidor via query (`q`) para que a paginação funcione sobre todo o volume de dados. A interface mantém estados locais para melhorar a experiência do usuário, evitando recarregamentos desnecessários.

### 3. Performance da Tabela: Scroll Infinito

- **Escolha:** Implementação de scroll infinito acoplado à paginação por offset do backend.
- **Justificativa:** A tabela carrega lotes de 20 operadoras conforme o usuário rola a página. Isso mantém o navegador rápido e responsivo, mesmo com milhares de registros.

### 4. Tratamento de Erros e Loading

- **Escolha:** Estados de feedback visual específicos
- **Justificativa:** Indicadores de loading para cada requisição assíncrona. Em caso de falha na API, o sistema exibe mensagens claras ao usuário, garantindo robustez.

## Funcionalidades Implementadas

- **Listagem Paginada:** Visualização eficiente de operadoras com carregamento dinâmico.
- **Busca em Tempo Real:** Filtro por Razão Social ou CNPJ diretamente na interface.
- **Dashboard de Estatísticas:** Visualização do Top 5 operadoras com maior volume financeiro e métricas globais.
- **Página de Detalhes:** Histórico completo de despesas, cálculo de Desvio Padrão e Média Trimestral.
- **Multi-aba:** Detalhes das operadoras abrem em novas abas para comparações rápidas.

## Como Executar

1. Certifique-se de que o Backend esteja rodando na porta 8000.
2. Instale as dependências:

```bash
    cd frontend
    npm install
```

3. Inicie o servidor de desenvolvimento:
```bash
    npm run dev
```

4. Acesse o endereço indicado no terminal (geralmente `http://localhost:5173`).
