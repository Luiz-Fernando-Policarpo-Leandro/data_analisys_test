<template>
  <div>
    <h1>Operadoras</h1>
    <input
      v-model="q"
      placeholder="Buscar por razão social ou CNPJ"
      @input="buscar"
    />

    <p v-if="loading">Carregando...</p>
    <p v-if="error">{{ error }}</p>

    <h2>Com Despesas</h2>
    <OperadorasTable :operadoras="comDespesas" />

    <h2>Sem Despesas</h2>
    <OperadorasTable :operadoras="semDespesas" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useOperadoras } from '../composables/useOperadoras'
import OperadorasTable from '../components/OperadorasTable.vue'

const q = ref('')
const { operadoras, loading, error, fetchOperadoras } = useOperadoras()

// Computed para separar
const comDespesas = computed(() =>
  operadoras.value.filter((op: any) => op.temDespesas)
)
const semDespesas = computed(() =>
  operadoras.value.filter((op: any) => !op.temDespesas)
)

function buscar() {
  fetchOperadoras(1, 50, q.value)
}

onMounted(() => fetchOperadoras())
</script>
