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

    <p v-if="loading && page === 1">Carregando...</p>
    <p v-if="error">{{ error }}</p>

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
import { ref, onMounted, nextTick } from 'vue'
import { useOperadoras } from '../composables/useOperadoras'
import OperadorasTable from '../components/OperadorasTable.vue'

const scrollContainer = ref<HTMLElement | null>(null)
const q = ref('')

const { operadoras, total, loading, error, page, loadMore, resetBusca } =
  useOperadoras()

function buscar() {
  resetBusca(q.value)
}

function onScroll() {
  if (!scrollContainer.value || loading.value) return

  const el = scrollContainer.value
  const bottomOfWindow =
    el.scrollTop + el.clientHeight >= el.scrollHeight - 80 // tolerância maior (80px)

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
  height: 80vh;
  overflow-y: auto;
  border: 1px solid #ccc;
  padding: 1rem;
  position: relative;
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
}
input::placeholder {
  color: #aaa;
} 
input:focus {
  outline: none;
  border-color: #42b883;
}

input:focus::placeholder {
  color: #ccc;
  quality: 0.8;
}



</style>