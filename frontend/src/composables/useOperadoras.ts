import { ref } from 'vue'
import { api } from '../api/http'

interface Operadora {
  id_operadora: number
  cnpj: string
  razao_social: string
  uf: string
  nome_fantasia?: string
  registro_ans?: string
  modalidade?: string
}

interface ApiResponse {
  data: Operadora[]
  total: number
}

export function useOperadoras() {
  const operadoras = ref<Operadora[]>([])
  const total = ref(0)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const page = ref(1)
  const limit = 20
  const q = ref('')
  const includeSemDespesas = ref(false)

  async function fetchOperadoras(reset = false) {
    if (loading.value) return

    loading.value = true
    error.value = null

    try {
      const response = await api.get<ApiResponse>('/operadoras', {
        params: {
          page: page.value,
          limit,
          q: q.value || undefined,
          include_sem_despesas: includeSemDespesas.value,
        },
      })

      if (reset) {
        operadoras.value = response.data.data
      } else {
        operadoras.value = [...operadoras.value, ...response.data.data]
      }

      total.value = response.data.total
    } catch (err: any) {
      error.value = err?.message || 'Erro ao carregar operadoras'
      console.error(err)
    } finally {
      loading.value = false
    }
  }

  function resetBusca(newQuery: string) {
    q.value = newQuery.trim()
    page.value = 1
    operadoras.value = [] // limpa visualmente mais rápido
    fetchOperadoras(true)
  }

  function loadMore() {
    if (loading.value) return
    if (operadoras.value.length >= total.value) return

    page.value += 1
    fetchOperadoras()
  }

  return {
    operadoras,
    total,
    loading,
    error,
    page,
    loadMore,
    resetBusca,
    includeSemDespesas,
  }
}