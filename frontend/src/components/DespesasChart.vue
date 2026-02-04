<template>
  <div class="chart-wrapper">
    <div v-if="loading" class="chart-overlay">Carregando gráfico...</div>
    
    <div v-if="!loading && hasNoData" class="chart-overlay">
      Nenhum dado de despesa encontrado para esta operadora.
    </div>

    <div class="chart-container" :class="{ 'is-loading': loading }">
      <canvas ref="canvas"></canvas>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import Chart from 'chart.js/auto'
import { api } from '../api/http'

const props = defineProps<{ cnpj: string }>()
const canvas = ref<HTMLCanvasElement | null>(null)
const loading = ref(true)
const hasNoData = ref(false)
let chartInstance: Chart | null = null

const renderChart = (data: any[]) => {
  if (!canvas.value) return
  if (chartInstance) chartInstance.destroy()

  chartInstance = new Chart(canvas.value, {
    type: 'line',
    data: {
      labels: data.map(d => `${d.ano} T${d.trimestre}`),
      datasets: [{
        label: 'Valor da Despesa (R$)',
        data: data.map(d => d.valor),
        borderColor: '#42b883',
        backgroundColor: 'rgba(66, 184, 131, 0.1)',
        fill: true,
        tension: 0.3,
        pointRadius: 4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        tooltip: {
          callbacks: {
            // CORREÇÃO DO ERRO: Verificamos se context.parsed.y existe
            label: (context) => {
              const valor = context.parsed.y;
              const formatado = valor !== null 
                ? valor.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' }) 
                : 'R$ 0,00';
              return `Despesa: ${formatado}`;
            }
          }
        }
      },
      scales: {
        y: {
          ticks: {
            callback: (value) => value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL', maximumFractionDigits: 0 })
          }
        }
      }
    }
  })
}

const fetchData = async () => {
  loading.value = true
  hasNoData.value = false
  try {
    const { data } = await api.get<any[]>(`/operadoras/${props.cnpj}/despesas`)
    
    if (data && data.length > 0) {
      renderChart(data)
    } else {
      hasNoData.value = true
    }
  } catch (error) {
    console.error("Erro ao carregar despesas:", error)
    hasNoData.value = true
  } finally {
    loading.value = false
  }
}

onMounted(fetchData)
watch(() => props.cnpj, fetchData)
</script>

<style scoped>
.chart-wrapper {
  position: relative;
  min-height: 350px;
  width: 100%;
  background: #ffffff;
  border-radius: 8px;
}

.chart-container {
  height: 350px;
  width: 100%;
  transition: opacity 0.3s;
}

.chart-container.is-loading {
  opacity: 0.2;
}

.chart-overlay {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: #64748b;
  font-weight: 500;
  text-align: center;
  z-index: 10;
}
</style>