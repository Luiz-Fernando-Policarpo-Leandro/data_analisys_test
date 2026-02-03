<template>
  <div class="stats-container">
    <h2>Estatísticas Globais</h2>

    <div class="cards-grid">
      <div class="card">
        <label>Total de Despesas</label>
        <p class="valor">R$ {{ formatarMoeda(stats?.total_despesas) }}</p>
      </div>
      <div class="card">
        <label>Média Global</label>
        <p class="valor">R$ {{ formatarMoeda(stats?.media_despesas) }}</p>
      </div>
    </div>

    <h3>Top 5 Operadoras</h3>
    <div class="lista-operadoras">
      <router-link 
        v-for="op in stats?.top_5_operadoras" 
        :key="op.cnpj"
        :to="`/operadoras/${op.cnpj}`" 
        target="_blank"
        class="item-operadora"
      >
        <div class="info">
          <span class="razao">{{ op.razao_social }}</span>
          <span class="cnpj">CNPJ: {{ op.cnpj }}</span>
        </div>
        <div class="montante">
          R$ {{ formatarMoeda(op.total_despesas) }}
        </div>
      </router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { api } from '../api/http'

const stats = ref<any>(null)

const formatarMoeda = (valor: number) => {
  if (!valor) return '0,00'
  return valor.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

onMounted(async () => {
  try {
    const { data } = await api.get('/estatisticas')
    stats.value = data
  } catch (err) {
    console.error("Erro ao carregar estatísticas", err)
  }
})
</script>

<style scoped>
.stats-container { padding: 20px; font-family: sans-serif; max-width: 1000px; margin: 0 auto; }
.cards-grid { display: flex; gap: 20px; margin-bottom: 30px; }
.card { background: #f8fafc; padding: 20px; border-radius: 12px; flex: 1; border: 1px solid #e2e8f0; }
.card label { display: block; font-size: 0.8rem; color: #64748b; text-transform: uppercase; margin-bottom: 5px; }
.valor { font-size: 1.6rem; font-weight: 800; color: #1e293b; }

.lista-operadoras { display: flex; flex-direction: column; gap: 12px; }
.item-operadora {
  display: flex; justify-content: space-between; align-items: center;
  padding: 16px; background: white; border: 1px solid #e2e8f0;
  border-radius: 8px; text-decoration: none; color: inherit;
  transition: all 0.2s ease;
}
.item-operadora:hover { border-color: #42b883; background: #f0fdf4; transform: translateY(-2px); }
.razao { display: block; font-weight: 700; color: #1e293b; }
.cnpj { font-size: 0.85rem; color: #64748b; }
.montante { font-weight: 800; color: #42b883; }
</style>