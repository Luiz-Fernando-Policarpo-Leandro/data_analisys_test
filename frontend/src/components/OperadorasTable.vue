<template>
  <div class="table-container">
    <table>
      <thead>
        <tr>
          <th>CNPJ</th>
          <th>Razão Social</th>
          <th>UF</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="op in operadoras" :key="op.cnpj">
          <td>{{ op.cnpj }}</td>
          <td>
            <router-link :to="`/operadoras/${op.cnpj}`" target="_blank">
              {{ op.razao_social }}
            </router-link>
          </td>
          <td>{{ op.uf }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  operadoras: any[]
}>()
</script>

<style scoped>
.table-container {
  overflow-x: auto;
  margin-top: 1rem;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th,
td {
  padding: 0.75rem;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

thead th {
  background-color: #f0f0f0;
  position: sticky;
  top: 0;
  z-index: 1;
}

/* Estilo para parecer um link de sistema profissional */
a {
  color: #42b883;
  text-decoration: none;
  font-weight: 500;
}

a:hover {
  text-decoration: underline;
}

tr:hover {
  background-color: #f9f9f9;
}
</style>