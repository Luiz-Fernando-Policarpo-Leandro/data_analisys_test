<template>
  <div class="table-container">
    <table class="custom-table">
      <thead>
        <tr>
          <th>CNPJ</th>
          <th>Razão Social</th>
          <th class="text-center">UF</th>
          <th class="text-right">Ações</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="op in operadoras" :key="op.cnpj" class="table-row">
          <td class="cnpj-cell">{{ formatarCnpj(op.cnpj) }}</td>
          <td class="razao-social-cell">
            <span class="razao-text">{{ op.razao_social }}</span>
            <small v-if="op.nome_fantasia" class="nome-fantasia">{{ op.nome_fantasia }}</small>
          </td>
          <td class="text-center">
            <span class="uf-badge">{{ op.uf }}</span>
          </td>
          <td class="text-right">
            <router-link 
              :to="{ name: 'operadora-detalhe', params: { cnpj: op.cnpj } }" 
              class="btn-detalhes"
            >
              Ver Detalhes
              <span class="icon">→</span>
            </router-link>
          </td>
        </tr>
      </tbody>
    </table>

    <div v-if="operadoras.length === 0" class="empty-state">
      Nenhuma operadora encontrada para os filtros aplicados.
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  operadoras: any[]
}>()

// Função utilitária para exibir o CNPJ formatado na tabela
const formatarCnpj = (val: string) => {
  return val.replace(/^(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})$/, "$1.$2.$3/$4-$5")
}
</script>

<style scoped>
.table-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  margin-top: 1.5rem;
  border: 1px solid #e2e8f0;
}

.custom-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.95rem;
}

th {
  background-color: #f8fafc;
  color: #64748b;
  font-weight: 600;
  text-transform: uppercase;
  font-size: 0.75rem;
  letter-spacing: 0.05em;
  padding: 1rem;
  border-bottom: 2px solid #e2e8f0;
}

td {
  padding: 1rem;
  border-bottom: 1px solid #f1f5f9;
  vertical-align: middle;
}

.table-row:hover {
  background-color: #f0fdf4; /* Verde bem clarinho ao passar o mouse */
}

.cnpj-cell {
  font-family: monospace;
  color: #475569;
}

.razao-social-cell {
  display: flex;
  flex-direction: column;
}

.razao-text {
  font-weight: 600;
  color: #1e293b;
}

.nome-fantasia {
  color: #94a3b8;
  font-size: 0.8rem;
}

.uf-badge {
  background: #e2e8f0;
  color: #475569;
  padding: 4px 8px;
  border-radius: 6px;
  font-weight: 700;
  font-size: 0.8rem;
}

.btn-detalhes {
  background-color: #42b883;
  color: white;
  padding: 6px 12px;
  border-radius: 6px;
  text-decoration: none;
  font-size: 0.85rem;
  font-weight: 600;
  transition: background 0.2s;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.btn-detalhes:hover {
  background-color: #33a06f;
}

.text-center { text-align: center; }
.text-right { text-align: right; }

.empty-state {
  padding: 3rem;
  text-align: center;
  color: #94a3b8;
}
</style>