<template>
  <div v-if="operadora">
    <h2>{{ operadora.razao_social }}</h2>
    <p>CNPJ: {{ operadora.cnpj }}</p>
    <p>UF: {{ operadora.uf }}</p>

    <DespesasChart :cnpj="cnpj" />
  </div>

  <p v-else>Carregando detalhes...</p>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { api } from '../api/http'
import DespesasChart from '../components/DespesasChart.vue'

const props = defineProps<{ cnpj: string }>()
const operadora = ref<any>(null)

onMounted(async () => {
  const { data } = await api.get(`/operadoras/${props.cnpj}`)
  operadora.value = data
})
</script>
