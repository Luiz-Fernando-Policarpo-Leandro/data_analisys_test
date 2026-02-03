<template>
  <div>
    <h1>Estatísticas Globais</h1>
    <p>Total de despesas: {{ estatisticas.total_despesas.toLocaleString() }}</p>
    <p>Média: {{ estatisticas.media_despesas.toLocaleString() }}</p>

    <h2>Top 5 Operadoras</h2>
    <ul>
      <li v-for="op in estatisticas.top_5_operadoras" :key="op.id_operadora">
        <router-link :to="`/operadoras/${op.cnpj}`">
          {{ op.razao_social }} — {{ op.total_despesas.toLocaleString() }}
        </router-link>
      </li>
    </ul>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted } from 'vue'
import { api } from '../api/http'

interface TopOperadora {
  id_operadora: number
  cnpj: string
  razao_social: string
  total_despesas: number
}

interface EstatisticasGlobais {
  total_despesas: number
  media_despesas: number
  top_5_operadoras: TopOperadora[]
}

const estatisticas = ref<EstatisticasGlobais>({
  total_despesas: 0,
  media_despesas: 0,
  top_5_operadoras: []
})

onMounted(async () => {
  try {
    const { data } = await api.get('/estatisticas')
    estatisticas.value = data
  } catch (err) {
    console.error('Erro ao buscar estatísticas', err)
  }
})
</script>
