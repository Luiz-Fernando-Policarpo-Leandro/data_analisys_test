import { ref } from 'vue'
import { api } from '../api/http'

export function useOperadoras() {
  const operadoras = ref<any[]>([])
  const total = ref(0)
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchOperadoras(page = 1, limit = 50, q = '') {
    loading.value = true
    error.value = null
    try {
      const { data } = await api.get('/operadoras', { params: { page, limit, q } })
      
      // Para cada operadora, consulta se tem despesas
      const withDespesas = await Promise.all(
        data.data.map(async (op: any) => {
          try {
            const res = await api.get(`/operadoras/${op.cnpj}/despesas`)
            return { ...op, temDespesas: res.data.length > 0 }
          } catch {
            return { ...op, temDespesas: false }
          }
        })
      )

      operadoras.value = withDespesas
      total.value = data.total
    } catch (err) {
      error.value = 'Erro ao carregar operadoras'
    } finally {
      loading.value = false
    }
  }

  return { operadoras, total, loading, error, fetchOperadoras }
}
