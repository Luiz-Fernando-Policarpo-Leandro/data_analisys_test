<template>
  <table>
    <thead>
      <tr>
        <th>CNPJ</th>
        <th>Razão Social</th>
        <th>UF</th>
        <th>Status</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="op in operadoras" :key="op.cnpj">
        <td>{{ op.cnpj }}</td>
            <td>
              <router-link :to="`/operadoras/${op.cnpj}`">{{ op.razao_social }}</router-link>
            </td>
        <td>{{ op.uf }}</td>
        <td>{{ op.temDespesas ? 'Com dados' : 'Sem dados' }}</td>
      </tr>
    </tbody>
  </table>
</template>

<script setup lang="ts">
defineProps<{ operadoras: any[] }>()
</script>
