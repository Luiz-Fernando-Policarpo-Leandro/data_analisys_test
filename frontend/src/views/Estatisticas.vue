<template>
  <div>
    <h2>Estatísticas Globais</h2>

    <p>Total de despesas: {{ stats?.total_despesas }}</p>
    <p>Média: {{ stats?.media_despesas }}</p>

    <h3>Top 5 Operadoras</h3>
    <ul>
      <li v-for="op in stats?.top_5_operadoras" :key="op.cnpj">
        {{ op.razao_social }} — {{ op.total_despesas }}
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { api } from '../api/http'

const stats = ref<any>(null)

onMounted(async () => {
  const { data } = await api.get('/estatisticas')
  stats.value = data
})
</script>
