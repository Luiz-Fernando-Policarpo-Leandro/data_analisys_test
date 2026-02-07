<template>
  <div
    ref="scrollContainer"
    class="scroll-container"
    @scroll.passive="onScroll"
  >
    <h1>Operadoras</h1>

    <input
      v-model="q"
      placeholder="Buscar por razão social ou CNPJ"
      @input="buscar"
    />

    <div class="filters">
      <label class="checkbox">
        <input
          v-model="includeSemDespesas"
          type="checkbox"
          @change="buscar"
        />
        Incluir operadoras sem despesas
      </label>
    </div>

    <p v-if="loading && page === 1">
      Carregando...
      <br />
      <small>
        Conectando no servidor (Render). Na primeira vez pode demorar {{ countdown }}s.
      </small>
    </p>

    <p v-if="error">
      {{ error }}
      <br />
      <small>
        Se for a primeira tentativa, aguarde alguns segundos e tente novamente.
      </small>
    </p>

    <OperadorasTable :operadoras="operadoras" />

    <div class="loading-more">
      <p v-if="loading && page > 1">Carregando mais...</p>
      <p v-if="operadoras.length >= total && operadoras.length > 0">
        Fim da lista
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, watch, onBeforeUnmount } from 'vue'
import { useOperadoras } from '../composables/useOperadoras'
import OperadorasTable from '../components/OperadorasTable.vue'

const scrollContainer = ref<HTMLElement | null>(null)
const q = ref('')

const {
  operadoras,
  total,
  loading,
  error,
  page,
  loadMore,
  resetBusca,
  includeSemDespesas
} = useOperadoras()

// ======================
// Contagem regressiva
// ======================
const countdown = ref(59)
let countdownInterval: number | null = null

function startCountdown() {
  stopCountdown()
  countdown.value = 59

  countdownInterval = window.setInterval(() => {
    if (countdown.value > 0) countdown.value--
  }, 1000)
}

function stopCountdown() {
  if (countdownInterval !== null) {
    clearInterval(countdownInterval)
    countdownInterval = null
  }
}

// Se começou a carregar a primeira página, inicia.
// Se terminou ou deu erro, para.
watch([loading, page, error], ([isLoading, currentPage, currentError]) => {
  if (currentPage === 1 && isLoading) {
    startCountdown()
    return
  }

  // Parar quando terminar OU se aparecer erro
  if (!isLoading || currentError) {
    stopCountdown()
  }
})

onBeforeUnmount(() => {
  stopCountdown()
})

// ======================

function buscar() {
  resetBusca(q.value)
}

function onScroll() {
  if (!scrollContainer.value || loading.value) return

  const el = scrollContainer.value
  const bottomOfWindow = el.scrollTop + el.clientHeight >= el.scrollHeight - 80

  if (bottomOfWindow) {
    loadMore()
  }
}

onMounted(async () => {
  resetBusca('')
  await nextTick()
})
</script>

<style scoped>
.scroll-container {
  height: 100vh;
  overflow-y: auto;
  padding: 2rem;
}

.loading-more {
  text-align: center;
  padding: 1rem 0;
  color: #666;
}

input {
  width: 100%;
  padding: 0.5rem;
  margin: 1rem 0;
  border: 1px solid #ddd;
  border-radius: 4px;
}

input:focus {
  outline: none;
  border-color: #42b883;
}

.filters {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 1rem;
}

.checkbox {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.95rem;
  color: #333;
  cursor: pointer;
}

.checkbox input[type="checkbox"] {
  width: 16px;
  height: 16px;
}
</style>
