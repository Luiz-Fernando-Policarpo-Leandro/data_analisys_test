<template>
  <canvas ref="canvas"></canvas>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import Chart from 'chart.js/auto'
import { api } from '../api/http'

interface Despesa {
  ano: number
  trimestre: number
  valor: number
}

const props = defineProps<{
  cnpj: string
}>()

const canvas = ref<HTMLCanvasElement | null>(null)

onMounted(async () => {
  const { data } = await api.get<Despesa[]>(
    `/operadoras/${props.cnpj}/despesas`
  )

  if (!canvas.value) return

  new Chart(canvas.value, {
    type: 'line',
    data: {
      labels: data.map((d: Despesa) => `${d.ano}T${d.trimestre}`),
      datasets: [
        {
          label: 'Despesas',
          data: data.map((d: Despesa) => d.valor)
        }
      ]
    }
  })
})


</script>
