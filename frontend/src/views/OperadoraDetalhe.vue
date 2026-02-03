<template>
  <div class="detalhe-container">
    <div v-if="loading" class="loading-state">Carregando dados...</div>

    <div v-else-if="operadora">
      <header class="header">
        <h1>{{ operadora.razao_social }}</h1>
        <div class="meta">
          <span><strong>CNPJ:</strong> {{ operadora.cnpj }}</span>
          <span><strong>UF:</strong> {{ operadora.uf }}</span>
          <span><strong>Registro ANS:</strong> {{ operadora.registro_ans }}</span>
        </div>
      </header>

      <section class="metrics-grid">
        <div class="metric-card">
          <label>Total de Despesas</label>
          <p>R$ {{ formatarMoeda(metricas?.total_despesas) }}</p>
        </div>
        <div class="metric-card">
          <label>Média Trimestral</label>
          <p>R$ {{ formatarMoeda(metricas?.media_despesas) }}</p>
        </div>
        <div class="metric-card accent">
          <label>Desvio Padrão</label>
          <p>R$ {{ formatarMoeda(metricas?.desvio_padrao) }}</p>
        </div>
      </section>

      <section class="chart-wrapper">
        <h3>Evolução das Despesas</h3>
        <DespesasChart :cnpj="cnpj" />
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { api } from '../api/http'
import DespesasChart from '../components/DespesasChart.vue'

const props = defineProps<{ cnpj: string }>()
const operadora = ref<any>(null)
const metricas = ref<any>(null)
const loading = ref(true)

const formatarMoeda = (valor: number) => {
  if (!valor) return '0,00'
  return valor.toLocaleString('pt-BR', { minimumFractionDigits: 2 })
}

async function carregarTudo() {
  loading.value = true
  try {
    const [resCadastro, resStats] = await Promise.all([
      api.get(`/operadoras/${props.cnpj}`),
      api.get(`/estatisticas/${props.cnpj}`)
    ])
    operadora.value = resCadastro.data
    metricas.value = resStats.data
  } catch (error) {
    console.error("Erro ao carregar detalhes:", error)
  } finally {
    loading.value = false
  }
}

onMounted(carregarTudo)
watch(() => props.cnpj, carregarTudo)
</script>

<style scoped>
.detalhe-container { padding: 40px; max-width: 1100px; margin: 0 auto; font-family: sans-serif; }
.loading-state { text-align: center; font-size: 1.2rem; color: #64748b; margin-top: 50px; }

.header { margin-bottom: 40px; }
.header h1 { font-size: 2rem; color: #0f172a; margin-bottom: 10px; }
.meta { display: flex; gap: 24px; color: #64748b; font-size: 0.9rem; }

.metrics-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 40px; }
.metric-card { background: white; border: 1px solid #e2e8f0; padding: 24px; border-radius: 12px; }
.metric-card label { display: block; font-size: 0.75rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; margin-bottom: 8px; }
.metric-card p { font-size: 1.5rem; font-weight: 800; color: #1e293b; margin: 0; }
.metric-card.accent { border-top: 4px solid #42b883; }

.chart-wrapper { background: #f8fafc; padding: 30px; border-radius: 16px; border: 1px solid #e2e8f0; }
.chart-wrapper h3 { margin-top: 0; margin-bottom: 20px; color: #334155; }

@media (max-width: 768px) {
  .metrics-grid { grid-template-columns: 1fr; }
}
</style>